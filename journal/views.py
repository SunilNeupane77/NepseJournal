from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Trade, TradeImage, Strategy
from .forms import TradeForm, TradeImageForm, StrategyForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from decimal import Decimal

@login_required
def trade_list(request):
    trades = Trade.objects.filter(user=request.user).order_by('-entry_date')
    return render(request, 'journal/trade_list.html', {'trades': trades})

@login_required
def trade_create(request):
    if request.method == 'POST':
        form = TradeForm(request.user, request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            trade.save()
            messages.success(request, 'Trade logged successfully!')
            return redirect('trade_list')
    else:
        form = TradeForm(request.user)
    return render(request, 'journal/trade_form.html', {'form': form, 'title': 'Log New Trade'})

@login_required
def trade_detail(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    return render(request, 'journal/trade_detail.html', {'trade': trade})

@login_required
def trade_update(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TradeForm(request.user, request.POST, instance=trade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Trade updated successfully!')
            return redirect('trade_detail', pk=pk)
    else:
        form = TradeForm(request.user, instance=trade)
    return render(request, 'journal/trade_form.html', {'form': form, 'title': 'Update Trade'})

@login_required
def trade_delete(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == 'POST':
        trade.delete()
        messages.success(request, 'Trade deleted successfully!')
        return redirect('trade_list')
    return render(request, 'journal/trade_confirm_delete.html', {'trade': trade})

@login_required
def strategy_list(request):
    strategies = Strategy.objects.filter(user=request.user)
    return render(request, 'journal/strategy_list.html', {'strategies': strategies})

@login_required
def strategy_create(request):
    if request.method == 'POST':
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.save(commit=False)
            strategy.user = request.user
            strategy.save()
            messages.success(request, 'Strategy created successfully!')
            return redirect('strategy_list')
    else:
        form = StrategyForm()
    return render(request, 'journal/strategy_form.html', {'form': form, 'title': 'Create New Strategy'})


@login_required
def generate_trade_report(request):
    """
    Generates a PDF report of the user's trading performance.
    """
    # Fetch closed trades for the user
    closed_trades = Trade.objects.filter(user=request.user, status='CLOSED').order_by('exit_date')

    pnl_values = [t.pnl for t in closed_trades if t.pnl is not None]

    total_trades = len(pnl_values)
    wins = [pnl for pnl in pnl_values if pnl > 0]
    losses = [pnl for pnl in pnl_values if pnl <= 0]

    winning_trades = len(wins)
    losing_trades = len(losses)

    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    total_pnl = sum(pnl_values) if pnl_values else Decimal('0.00')

    average_win = sum(wins) / len(wins) if wins else Decimal('0.00')
    average_loss = sum(losses) / len(losses) if losses else Decimal('0.00')
    
    largest_win = max(wins) if wins else Decimal('0.00')
    largest_loss = min(losses) if losses else Decimal('0.00')

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trade_performance_report.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Draw things on the PDF.
    p.setFont("Helvetica-Bold", 16)
    p.drawString(1 * inch, height - 1 * inch, f"Trade Performance Report for {request.user.username}")

    p.setFont("Helvetica", 12)
    y_position = height - 1.5 * inch

    def draw_metric(label, value, y_pos):
        p.drawString(1 * inch, y_pos, f"{label}:")
        p.drawString(3.5 * inch, y_pos, str(value))
        return y_pos - 0.3 * inch

    y_position = draw_metric("Total Closed Trades", total_trades, y_position)
    y_position = draw_metric("Winning Trades", winning_trades, y_position)
    y_position = draw_metric("Losing Trades", losing_trades, y_position)
    y_position = draw_metric("Win Rate", f"{win_rate:.2f}%", y_position)
    y_position = draw_metric("Total P&L", f"{total_pnl:.2f}", y_position)
    y_position = draw_metric("Average Win", f"{average_win:.2f}", y_position)
    y_position = draw_metric("Average Loss", f"{average_loss:.2f}", y_position)
    y_position = draw_metric("Largest Win", f"{largest_win:.2f}", y_position)
    y_position = draw_metric("Largest Loss", f"{largest_loss:.2f}", y_position)

    # Close the PDF object cleanly.
    p.showPage()
    p.save()

    return response
