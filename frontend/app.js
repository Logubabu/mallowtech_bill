const API_BASE = "http://localhost:8000/api";

// Page 1 logic
const addBtn = document.getElementById('addBtn');
if (addBtn) {
    addBtn.addEventListener('click', () => {
        const productSection = document.getElementById('productSection');
        const div = document.createElement('div');
        div.className = 'product-item';
        div.innerHTML = `
            <input type="text" placeholder="Product ID" class="prod-id" required>
            <input type="number" placeholder="Quantity" class="prod-qty" required min="1">
        `;
        productSection.appendChild(div);
    });
}

const billForm = document.getElementById('billForm');
if (billForm) {
    billForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const items = [];
        document.querySelectorAll('.product-item').forEach(el => {
            items.push({
                product_id: el.querySelector('.prod-id').value,
                quantity: parseInt(el.querySelector('.prod-qty').value)
            });
        });

        const denominations = {
            "500": document.getElementById('den-500').value || 0,
            "50": document.getElementById('den-50').value || 0,
            "20": document.getElementById('den-20').value || 0,
            "10": document.getElementById('den-10').value || 0,
            "5": document.getElementById('den-5').value || 0,
            "2": document.getElementById('den-2').value || 0,
            "1": document.getElementById('den-1').value || 0
        };

        const cashPaid = parseFloat(document.getElementById('cashPaid').value);

        const payload = {
            customer_email: email,
            items: items,
            denominations: denominations,
            cash_paid: cashPaid
        };

        try {
            const res = await fetch(`${API_BASE}/bills`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!res.ok) {
                const data = await res.json();
                alert('Error: ' + data.detail);
                return;
            }
            const data = await res.json();
            localStorage.setItem('currentBill', JSON.stringify(data));
            window.location.href = 'bill.html';
        } catch (error) {
            console.error(error);
            alert("Error submitting bill");
        }
    });
}

// Page 2 logic
const billDataStr = localStorage.getItem('currentBill');
if (window.location.pathname.includes('bill.html') && billDataStr) {
    const data = JSON.parse(billDataStr);
    
    document.getElementById('cEmail').innerText = data.customer_email;
    
    const tbody = document.getElementById('billItems');
    data.items.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.product_id}</td>
            <td>${item.unit_price}</td>
            <td>${item.quantity}</td>
            <td>${item.purchase_price}</td>
            <td>${item.tax_for_item}%</td>
            <td>${item.tax_payable}</td>
            <td>${item.total_price}</td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('totalWithoutTax').innerText = data.total_price_without_tax.toFixed(2);
    document.getElementById('totalTax').innerText = data.total_tax_payable.toFixed(2);
    document.getElementById('netPrice').innerText = data.net_price.toFixed(2);
    document.getElementById('roundedPrice').innerText = data.rounded_net_price.toFixed(2);
    document.getElementById('balance').innerText = data.balance_payable.toFixed(2);

    const denomsDiv = document.getElementById('balanceDenoms');
    for (const [d, count] of Object.entries(data.balance_denominations)) {
        if (count > 0) {
            denomsDiv.innerHTML += `<div>${d}: ${count}</div>`;
        }
    }
}

// History logic
const searchHistoryBtn = document.getElementById('searchHistory');
if (searchHistoryBtn) {
    searchHistoryBtn.addEventListener('click', async () => {
        const email = document.getElementById('historyEmail').value;
        const res = await fetch(`${API_BASE}/bills?email=${email}`);
        if (res.ok) {
            const bills = await res.json();
            const list = document.getElementById('historyList');
            list.innerHTML = '';
            bills.forEach(b => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="#" onclick="viewBill(${b.id})">Bill #${b.id} - ${b.created_at} - Net: ${b.net_price}</a>`;
                list.appendChild(li);
            });
        }
    });
}

async function viewBill(id) {
    const res = await fetch(`${API_BASE}/bills/${id}`);
    if (res.ok) {
        const data = await res.json();
        localStorage.setItem('currentBill', JSON.stringify(data));
        window.location.href = 'bill.html';
    }
}
