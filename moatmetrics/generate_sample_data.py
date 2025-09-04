"""
Generate sample data for testing MoatMetrics MVP.

This script creates sample CSV files for clients, invoices, 
time logs, and licenses to demonstrate the system capabilities.
"""

import csv
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Sample data configuration
NUM_CLIENTS = 10
NUM_INVOICES_PER_CLIENT = 5
NUM_TIME_LOGS_PER_CLIENT = 20
NUM_LICENSES_PER_CLIENT = 3

# Industries
INDUSTRIES = ["Technology", "Healthcare", "Finance", "Retail", "Manufacturing", "Education", "Legal", "Real Estate"]

# Products for licenses
SOFTWARE_PRODUCTS = [
    ("Microsoft 365", "Microsoft", 20, 150),
    ("Adobe Creative Cloud", "Adobe", 10, 50),
    ("Salesforce CRM", "Salesforce", 25, 125),
    ("Slack", "Slack", 5, 25),
    ("Zoom", "Zoom", 10, 15),
    ("GitHub Enterprise", "GitHub", 15, 40),
    ("AWS", "Amazon", 100, 500),
    ("Google Workspace", "Google", 15, 20),
    ("Dropbox Business", "Dropbox", 8, 15),
    ("Jira", "Atlassian", 10, 25)
]

# Staff members
STAFF_MEMBERS = [
    ("John Smith", "john.smith@moatmetrics.com", 150),
    ("Jane Doe", "jane.doe@moatmetrics.com", 175),
    ("Mike Johnson", "mike.johnson@moatmetrics.com", 125),
    ("Sarah Williams", "sarah.williams@moatmetrics.com", 140),
    ("David Brown", "david.brown@moatmetrics.com", 160)
]

# Project names
PROJECT_NAMES = [
    "Infrastructure Upgrade",
    "Security Audit",
    "Cloud Migration",
    "Software Implementation",
    "Support Services",
    "Network Optimization",
    "Data Backup Setup",
    "Compliance Review"
]


def generate_clients():
    """Generate sample client data."""
    print("Generating clients...")
    clients = []
    
    for i in range(1, NUM_CLIENTS + 1):
        client = {
            "name": f"Client {i:03d} Corp",
            "industry": random.choice(INDUSTRIES),
            "contact_email": f"contact@client{i:03d}.com",
            "contact_phone": f"555{random.randint(1000000, 9999999):07d}",
            "is_active": random.random() > 0.1  # 90% active
        }
        clients.append(client)
    
    # Save to CSV
    file_path = Path("moatmetrics/data/raw/clients.csv")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=clients[0].keys())
        writer.writeheader()
        writer.writerows(clients)
    
    print(f"✓ Generated {len(clients)} clients")
    return clients


def generate_invoices(clients):
    """Generate sample invoice data."""
    print("Generating invoices...")
    invoices = []
    
    for idx, client in enumerate(clients, 1):
        for inv_num in range(1, NUM_INVOICES_PER_CLIENT + 1):
            # Generate date in last 6 months
            days_ago = random.randint(0, 180)
            invoice_date = datetime.now() - timedelta(days=days_ago)
            due_date = invoice_date + timedelta(days=30)
            
            # Generate line items
            num_lines = random.randint(1, 5)
            lines = []
            for _ in range(num_lines):
                lines.append({
                    "description": random.choice([
                        "Managed IT Services",
                        "Cloud Storage",
                        "Security Monitoring",
                        "Software License",
                        "Consulting Hours",
                        "Hardware Maintenance"
                    ]),
                    "quantity": random.randint(1, 10),
                    "unit_price": random.randint(50, 500),
                    "tax_rate": 0.08,
                    "discount": random.randint(0, 50)
                })
            
            total = sum((l["quantity"] * l["unit_price"] - l["discount"]) * 1.08 for l in lines)
            
            invoice = {
                "client_name": client["name"],
                "invoice_number": f"INV-{idx:03d}-{inv_num:03d}",
                "date": invoice_date.strftime("%Y-%m-%d"),
                "due_date": due_date.strftime("%Y-%m-%d"),
                "currency": "USD",
                "total_amount": round(total, 2),
                "status": random.choice(["paid", "pending", "overdue"]),
                "lines_json": json.dumps(lines)
            }
            invoices.append(invoice)
    
    # Save to CSV
    file_path = Path("moatmetrics/data/raw/invoices.csv")
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=invoices[0].keys())
        writer.writeheader()
        writer.writerows(invoices)
    
    print(f"✓ Generated {len(invoices)} invoices")
    return invoices


def generate_time_logs(clients):
    """Generate sample time log data."""
    print("Generating time logs...")
    time_logs = []
    
    for client in clients:
        for _ in range(NUM_TIME_LOGS_PER_CLIENT):
            # Random date in last 3 months
            days_ago = random.randint(0, 90)
            log_date = datetime.now() - timedelta(days=days_ago)
            
            staff = random.choice(STAFF_MEMBERS)
            
            time_log = {
                "client_name": client["name"],
                "staff_name": staff[0],
                "staff_email": staff[1],
                "date": log_date.strftime("%Y-%m-%d"),
                "hours": round(random.uniform(0.5, 8), 1),
                "rate": staff[2],
                "project_name": random.choice(PROJECT_NAMES),
                "task_description": random.choice([
                    "System maintenance and updates",
                    "Troubleshooting network issues",
                    "User support and training",
                    "Security configuration",
                    "Backup verification",
                    "Performance optimization"
                ]),
                "billable": random.random() > 0.15  # 85% billable
            }
            time_logs.append(time_log)
    
    # Save to CSV
    file_path = Path("moatmetrics/data/raw/time_logs.csv")
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=time_logs[0].keys())
        writer.writeheader()
        writer.writerows(time_logs)
    
    print(f"✓ Generated {len(time_logs)} time logs")
    return time_logs


def generate_licenses(clients):
    """Generate sample license data."""
    print("Generating licenses...")
    licenses = []
    
    for client in clients:
        # Select random products
        selected_products = random.sample(SOFTWARE_PRODUCTS, min(NUM_LICENSES_PER_CLIENT, len(SOFTWARE_PRODUCTS)))
        
        for product_info in selected_products:
            product, vendor, min_seats, max_seats = product_info
            seats_purchased = random.randint(min_seats, max_seats)
            
            # Simulate various utilization rates
            utilization_factor = random.choice([0.2, 0.3, 0.5, 0.7, 0.85, 0.95, 1.0])
            seats_used = min(int(seats_purchased * utilization_factor), seats_purchased)
            
            # Generate dates
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=365)  # Annual licenses
            
            license = {
                "client_name": client["name"],
                "product": product,
                "vendor": vendor,
                "license_type": random.choice(["subscription", "perpetual"]),
                "seats_purchased": seats_purchased,
                "seats_used": seats_used,
                "cost_per_seat": random.randint(10, 200),
                "total_cost": seats_purchased * random.randint(10, 200) * 12,  # Annual cost
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "is_active": end_date > datetime.now(),
                "auto_renew": random.random() > 0.3  # 70% auto-renew
            }
            licenses.append(license)
    
    # Save to CSV
    file_path = Path("moatmetrics/data/raw/licenses.csv")
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=licenses[0].keys())
        writer.writeheader()
        writer.writerows(licenses)
    
    print(f"✓ Generated {len(licenses)} licenses")
    return licenses


def main():
    """Generate all sample data files."""
    print("\n" + "="*50)
    print("MoatMetrics Sample Data Generator")
    print("="*50 + "\n")
    
    # Generate data
    clients = generate_clients()
    invoices = generate_invoices(clients)
    time_logs = generate_time_logs(clients)
    licenses = generate_licenses(clients)
    
    # Summary statistics
    print("\n" + "-"*50)
    print("Sample Data Summary:")
    print("-"*50)
    
    # Calculate some interesting metrics
    total_revenue = sum(i["total_amount"] for i in invoices if i["status"] == "paid")
    total_hours = sum(t["hours"] for t in time_logs)
    avg_license_utilization = sum(
        (l["seats_used"] / l["seats_purchased"] * 100) if l["seats_purchased"] > 0 else 0
        for l in licenses
    ) / len(licenses)
    
    print(f"• Total Clients: {len(clients)}")
    print(f"• Total Invoices: {len(invoices)}")
    print(f"• Total Time Logs: {len(time_logs)}")
    print(f"• Total Licenses: {len(licenses)}")
    print(f"• Total Revenue (Paid): ${total_revenue:,.2f}")
    print(f"• Total Hours Logged: {total_hours:,.1f}")
    print(f"• Average License Utilization: {avg_license_utilization:.1f}%")
    
    # Identify interesting patterns for demo
    print("\n" + "-"*50)
    print("Interesting Patterns in Data (for demo):")
    print("-"*50)
    
    # Find underutilized licenses
    underutilized = [l for l in licenses if l["seats_purchased"] > 0 and 
                     (l["seats_used"] / l["seats_purchased"]) < 0.5]
    if underutilized:
        print(f"• {len(underutilized)} licenses are underutilized (<50%)")
        print(f"  - Example: {underutilized[0]['product']} at {underutilized[0]['client_name']}")
    
    # Find high-value clients
    client_revenue = {}
    for inv in invoices:
        if inv["status"] == "paid":
            client_revenue[inv["client_name"]] = client_revenue.get(inv["client_name"], 0) + inv["total_amount"]
    
    if client_revenue:
        top_client = max(client_revenue.items(), key=lambda x: x[1])
        print(f"• Top revenue client: {top_client[0]} (${top_client[1]:,.2f})")
    
    # Find overworked staff
    staff_hours = {}
    for log in time_logs:
        staff_hours[log["staff_name"]] = staff_hours.get(log["staff_name"], 0) + log["hours"]
    
    if staff_hours:
        busiest_staff = max(staff_hours.items(), key=lambda x: x[1])
        print(f"• Busiest staff member: {busiest_staff[0]} ({busiest_staff[1]:.1f} hours)")
    
    print("\n" + "="*50)
    print("✓ Sample data generation complete!")
    print("  Files saved to: moatmetrics/data/raw/")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
