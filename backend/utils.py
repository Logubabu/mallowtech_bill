import asyncio

def calculate_balance_denominations(balance: float, available_denominations: dict):
    # available_denominations
    denoms = [500, 50, 20, 10, 5, 2, 1]
    result = {}
    remaining = int(balance) # using int since denominations are integers
    
    for d in denoms:
        d_str = str(d)
        if remaining >= d:
            count = remaining // d
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
