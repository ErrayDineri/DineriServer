# passwordmanager/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import VaultEntryForm, CSVImportForm
from .models import VaultEntry
from .services.utils import derive_key, encrypt_password, decrypt_password
from django.db import transaction
import os
import csv
import io
import time
import hashlib

def get_user_salt(user_id):
    """Generate a consistent salt for a user based on their ID and a secret"""
    # Use user ID + a secret string to generate deterministic but secure salt
    secret_component = "dineri_password_vault_salt_v1"  # Version it for future changes
    salt_input = f"{user_id}_{secret_component}".encode()
    return hashlib.sha256(salt_input).digest()[:16]  # Use first 16 bytes as salt

@login_required
def add_entry(request):
    if request.method == 'POST':
        form = VaultEntryForm(request.POST)
        if form.is_valid():
            salt = get_user_salt(request.user.id)  # Use shared salt per user
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
        entries = VaultEntry.objects.filter(user=request.user).select_related()
        decrypted = []
        
        if entries:
            # Since all entries for a user share the same salt, derive key once
            try:
                key_derivation_start = time.time()
                shared_key = derive_key(master_pw, get_user_salt(request.user.id))
                key_derivation_time = round((time.time() - key_derivation_start) * 1000, 2)
                
                # Decrypt all entries using the shared key
                decryption_start = time.time()
                for entry in entries:
                    try:
                        decrypted_pw = decrypt_password(entry.encrypted_password, entry.nonce, shared_key)
                        decrypted.append((entry, decrypted_pw))
                    except Exception:
                        decrypted.append((entry, 'Invalid master password'))
                
                decryption_time = round((time.time() - decryption_start) * 1000, 2)
                
            except Exception:
                # If key derivation fails, mark all entries as invalid
                for entry in entries:
                    decrypted.append((entry, 'Invalid master password'))
                key_derivation_time = 0
                decryption_time = 0
        else:
            key_derivation_time = 0
            decryption_time = 0
        
        end_time = time.time()
        total_time = round((end_time - start_time) * 1000, 2)
        
        # Remove timing messages for cleaner UI
        # messages.info(request, f'🔓 Vault decrypted in {total_time}ms ({len(entries)} entries, 1 key derivation)')
        # messages.info(request, f'⚡ Breakdown: Key derivation: {key_derivation_time}ms, Decryption: {decryption_time}ms')
        
        return render(request, 'passwordmanager/vault.html', {
            'entries': decrypted,
            'decrypt_time': total_time,
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
                csv_data = list(csv.DictReader(io.StringIO(decoded_file)))
                file_read_time = round((time.time() - file_read_start) * 1000, 2)
                
                imported_count = 0
                skipped_count = 0
                error_count = 0
                
                processing_start = time.time()
                
                # Pre-fetch existing entries for duplicate checking
                existing_entries = set()
                if not allow_duplicates:
                    existing_entries = set(
                        VaultEntry.objects.filter(user=request.user)
                        .values_list('site_name', 'username')
                    )
                
                # Use shared salt for all entries for this user
                shared_salt = get_user_salt(request.user.id)
                shared_key = derive_key(master_password, shared_salt)
                
                # Prepare entries for bulk creation
                entries_to_create = []
                
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
                            if (site_name, username) in existing_entries:
                                skipped_count += 1
                                continue
                        
                        # Encrypt password using shared key
                        nonce, encrypted_pw = encrypt_password(password, shared_key)
                        
                        # Add to bulk creation list
                        entries_to_create.append(VaultEntry(
                            user=request.user,
                            site_name=site_name,
                            url=url if url else '',
                            username=username,
                            encrypted_password=encrypted_pw,
                            nonce=nonce,
                            salt=shared_salt  # Use shared salt
                        ))
                        imported_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        continue
                
                # Bulk create all entries at once using transaction
                if entries_to_create:
                    with transaction.atomic():
                        VaultEntry.objects.bulk_create(entries_to_create, batch_size=500)
                
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
