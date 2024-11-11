from django.shortcuts import render, redirect
from .models import Checklist
from .form import ChecklistForm

def checklist_view(request):
    items = Checklist.objects.all()
    
    context = {
        'items': items
    }

    return render(request, 'app/checklist.html', context)

def add_item_view(request):
    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('checklist')
    else:
        form = ChecklistForm()
    return render(request, 'app/add_item.html', {'form': form})
