# passwordmanager/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import VaultEntryForm, CSVImportForm
from .models import VaultEntry
from .services.utils import derive_key, encrypt_password, decrypt_password
import os
import csv
import io
import time

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = VaultEntryForm(request.POST)
        if form.is_valid():
            salt = os.urandom(16)
            key = derive_key(form.cleaned_data['master_password'], salt)
            nonce, encrypted_pw = encrypt_password(form.cleaned_data['password'], key)
            
            VaultEntry.objects.create(
                user=request.user,
                site_name=form.cleaned_data['site_name'],
                url=form.cleaned_data['url'],
                username=form.cleaned_data['username'],
                encrypted_password=encrypted_pw,
                nonce=nonce,
                salt=salt
            )
            return redirect('vault')
    else:
        form = VaultEntryForm()
    return render(request, 'passwordmanager/add_entry.html', {'form': form})


@login_required
def vault(request):
    if request.method == 'POST':
        start_time = time.time()
        
        master_pw = request.POST['master_password']
        entries = VaultEntry.objects.filter(user=request.user)
        decrypted = []
        
        for entry in entries:
            try:
                key = derive_key(master_pw, entry.salt)
                decrypted_pw = decrypt_password(entry.encrypted_password, entry.nonce, key)
                decrypted.append((entry, decrypted_pw))
            except Exception as e:
                decrypted.append((entry, 'Invalid master password'))
        
        end_time = time.time()
        decrypt_time = round((end_time - start_time) * 1000, 2)  # Convert to milliseconds
        
        messages.info(request, f'🔓 Vault decrypted in {decrypt_time}ms ({len(entries)} entries)')
        
        return render(request, 'passwordmanager/vault.html', {
            'entries': decrypted,
            'decrypt_time': decrypt_time,
            'entries_count': len(entries)
        })
    return render(request, 'passwordmanager/vault_login.html')


@login_required
def import_csv(request):
    if request.method == 'POST':
        start_time = time.time()
        
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            master_password = form.cleaned_data['master_password']
            allow_duplicates = form.cleaned_data['allow_duplicates']
            
            try:
                # Read CSV file
                file_read_start = time.time()
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                file_read_time = round((time.time() - file_read_start) * 1000, 2)
                
                imported_count = 0
                skipped_count = 0
                error_count = 0
                
                processing_start = time.time()
                
                for row in csv_data:
                    try:
                        # Extract data from CSV row
                        site_name = row.get('name', '').strip()
                        url = row.get('login_uri', '').strip()
                        username = row.get('login_username', '').strip()
                        password = row.get('login_password', '').strip()
                        
                        # Skip empty entries
                        if not site_name or not password:
                            skipped_count += 1
                            continue
                        
                        # Check for duplicates if not allowing them
                        if not allow_duplicates:
                            existing = VaultEntry.objects.filter(
                                user=request.user,
                                site_name=site_name,
                                username=username
                            ).exists()
                            if existing:
                                skipped_count += 1
                                continue
                        
                        # Encrypt password
                        salt = os.urandom(16)
                        key = derive_key(master_password, salt)
                        nonce, encrypted_pw = encrypt_password(password, key)
                        
                        # Create vault entry
                        VaultEntry.objects.create(
                            user=request.user,
                            site_name=site_name,
                            url=url if url else '',
                            username=username,
                            encrypted_password=encrypted_pw,
                            nonce=nonce,
                            salt=salt
                        )
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        continue
                
                processing_time = round((time.time() - processing_start) * 1000, 2)
                total_time = round((time.time() - start_time) * 1000, 2)
                
                # Show results with timing info
                if imported_count > 0:
                    messages.success(request, f'✅ Successfully imported {imported_count} password entries in {total_time}ms')
                    messages.info(request, f'📊 Timing: File read: {file_read_time}ms, Processing: {processing_time}ms')
                if skipped_count > 0:
                    messages.info(request, f'⏭️ Skipped {skipped_count} entries (empty or duplicate)')
                if error_count > 0:
                    messages.warning(request, f'⚠️ {error_count} entries had errors and were not imported')
                
                return redirect('vault')
                
            except Exception as e:
                total_time = round((time.time() - start_time) * 1000, 2)
                messages.error(request, f'❌ Error processing CSV file in {total_time}ms: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CSVImportForm()
    
    return render(request, 'passwordmanager/import_csv.html', {'form': form})
