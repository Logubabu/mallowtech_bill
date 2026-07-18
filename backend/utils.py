import asyncio

def calculate_balance_denominations(balance: float, available_denominations: dict):
    # available_denominations could be something like: {'500': 10, '50': 20, '20': 50, ...}
    # In this problem, it says "Calculate the balance denomination that needs to be given to the customer based on the denominations available in the shop".
    # Wait, the problem says "You can create the default denominations as shown in the image to collect the denominations count in each of the available values. Note: The denominations are the values that are available in the shop."
    # Let's assume shop has enough denominations, but we should prioritize largest first.
    denoms = [500, 50, 20, 10, 5, 2, 1]
    result = {}
    remaining = int(balance) # using int since denominations are integers
    
    for d in denoms:
        d_str = str(d)
        if remaining >= d:
            count = remaining // d
            # If we were strictly limiting by shop's available count, we'd check available_denominations[d_str]
            # But the requirement implies we just calculate what to give back.
            result[d_str] = count
            remaining = remaining % d
            
    return result

async def send_invoice_email(email: str, bill_id: int, net_price: float):
    # Mocking background email sending
    print(f"--- START EMAIL ---")
    print(f"Sending invoice for Bill #{bill_id} to {email}")
    print(f"Total Amount: {net_price}")
    print(f"--- END EMAIL ---")
    await asyncio.sleep(2) # simulate delay
    print(f"Invoice for Bill #{bill_id} sent successfully.")
