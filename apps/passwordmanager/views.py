# passwordmanager/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import VaultEntryForm
from .models import VaultEntry
from .services.utils import derive_key, encrypt_password, decrypt_password
import os

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
        return render(request, 'passwordmanager/vault.html', {'entries': decrypted})
    return render(request, 'passwordmanager/vault_login.html')
