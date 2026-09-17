import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from config import Config
from models import db, User, Customer, Ticket, TicketComment, ActivityLog

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

STATUSES = ["Open", "In Progress", "Resolved"]
PRIORITIES = ["Low", "Medium", "High"]

def current_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "authentication required"}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user or user.role not in roles:
                if request.path.startswith("/api/"):
                    return jsonify({"error": "forbidden"}), 403
                flash("You do not have permission for this action.", "error")
                return redirect(url_for("index"))
            return view(*args, **kwargs)
        return wrapped
    return decorator

def log_activity(action, entity, entity_id=None):
    uid = session.get("user_id")
    db.session.add(ActivityLog(user_id=uid, action=action, entity=entity, entity_id=entity_id))
    db.session.commit()

@app.context_processor
def inject_globals():
    return {"current_user": current_user(), "now": datetime.utcnow()}

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    stats = {
        "customers": Customer.query.filter_by(active=True).count(),
        "open": Ticket.query.filter_by(status="Open").count(),
        "progress": Ticket.query.filter_by(status="In Progress").count(),
        "resolved": Ticket.query.filter_by(status="Resolved").count(),
        "high": Ticket.query.filter_by(priority="High").filter(Ticket.status != "Resolved").count(),
    }
    recent = Ticket.query.order_by(Ticket.created_at.desc()).limit(8).all()
    return render_template("dashboard.html", stats=stats, recent=recent)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            log_activity("Logged in", "User", user.id)
            return redirect(url_for("index"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    uid = session.get("user_id")
    session.clear()
    if uid:
        # no commit needed for logout activity
        pass
    return redirect(url_for("login"))

@app.route("/customers")
@login_required
def customers():
    q = request.args.get("q", "").strip()
    query = Customer.query
    if q:
        query = query.filter((Customer.company_name.ilike(f"%{q}%")) | (Customer.contact_person.ilike(f"%{q}%")))
    return render_template("customers.html", customers=query.order_by(Customer.company_name).all(), q=q)

@app.route("/customers/new", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Manager")
def new_customer():
    if request.method == "POST":
        customer = Customer(
            company_name=request.form["company_name"].strip(),
            contact_person=request.form["contact_person"].strip(),
            email=request.form["email"].strip().lower(),
            phone=request.form["phone"].strip(),
            industry=request.form["industry"].strip(),
        )
        db.session.add(customer); db.session.commit()
        log_activity("Created customer", "Customer", customer.id)
        flash("Customer created successfully.", "success")
        return redirect(url_for("customers"))
    return render_template("customer_form.html", customer=None)

@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Manager")
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == "POST":
        customer.company_name = request.form["company_name"].strip()
        customer.contact_person = request.form["contact_person"].strip()
        customer.email = request.form["email"].strip().lower()
        customer.phone = request.form["phone"].strip()
        customer.industry = request.form["industry"].strip()
        db.session.commit()
        log_activity("Updated customer", "Customer", customer.id)
        flash("Customer updated.", "success")
        return redirect(url_for("customers"))
    return render_template("customer_form.html", customer=customer)

@app.route("/tickets")
@login_required
def tickets():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    query = Ticket.query
    if q:
        query = query.filter((Ticket.title.ilike(f"%{q}%")) | (Ticket.ticket_number.ilike(f"%{q}%")))
    if status in STATUSES: query = query.filter_by(status=status)
    if priority in PRIORITIES: query = query.filter_by(priority=priority)
    return render_template("tickets.html", tickets=query.order_by(Ticket.created_at.desc()).all(),
                           q=q, status=status, priority=priority, statuses=STATUSES, priorities=PRIORITIES)

@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
def new_ticket():
    customers = Customer.query.filter_by(active=True).order_by(Customer.company_name).all()
    users = User.query.filter(User.role.in_(["Manager", "Employee"])).order_by(User.name).all()
    if request.method == "POST":
        title = request.form["title"].strip()
        if not title or not request.form["customer_id"]:
            flash("Title and customer are required.", "error")
            return render_template("ticket_form.html", customers=customers, users=users, ticket=None, priorities=PRIORITIES)
        ticket = Ticket(
            title=title,
            description=request.form["description"].strip(),
            priority=request.form["priority"],
            customer_id=int(request.form["customer_id"]),
            assigned_to=int(request.form["assigned_to"]) if request.form["assigned_to"] else None,
        )
        db.session.add(ticket); db.session.commit()
        ticket.ticket_number = f"TKT-{ticket.id:05d}"
        db.session.commit()
        log_activity("Created ticket", "Ticket", ticket.id)
        flash("Support ticket created.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket.id))
    return render_template("ticket_form.html", customers=customers, users=users, ticket=None, priorities=PRIORITIES)

@app.route("/tickets/<int:ticket_id>")
@login_required
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template("ticket_detail.html", ticket=ticket, statuses=STATUSES, users=User.query.filter(User.role.in_(["Manager","Employee"])).all())

@app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
@login_required
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = request.form["status"] if request.form["status"] in STATUSES else ticket.status
    ticket.priority = request.form["priority"] if request.form["priority"] in PRIORITIES else ticket.priority
    ticket.assigned_to = int(request.form["assigned_to"]) if request.form["assigned_to"] else None
    db.session.commit()
    log_activity("Updated ticket", "Ticket", ticket.id)
    flash("Ticket updated.", "success")
    return redirect(url_for("ticket_detail", ticket_id=ticket.id))

@app.route("/tickets/<int:ticket_id>/comments", methods=["POST"])
@login_required
def add_comment(ticket_id):
    Ticket.query.get_or_404(ticket_id)
    body = request.form["body"].strip()
    if body:
        db.session.add(TicketComment(ticket_id=ticket_id, user_id=session["user_id"], body=body))
        db.session.commit()
        log_activity("Added ticket comment", "Ticket", ticket_id)
    return redirect(url_for("ticket_detail", ticket_id=ticket_id))

# Operational health check
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "business-support-platform"})

# REST API
@app.route("/api/tickets", methods=["GET"])
@login_required
def api_tickets():
    status = request.args.get("status")
    query = Ticket.query
    if status in STATUSES: query = query.filter_by(status=status)
    return jsonify([t.to_dict() for t in query.order_by(Ticket.created_at.desc()).all()])

@app.route("/api/tickets", methods=["POST"])
@login_required
def api_create_ticket():
    data = request.get_json(silent=True) or {}
    required = ["title", "customer_id"]
    missing = [x for x in required if not data.get(x)]
    if missing: return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400
    if not Customer.query.get(data["customer_id"]):
        return jsonify({"error": "customer not found"}), 404
    priority = data.get("priority", "Medium")
    if priority not in PRIORITIES: return jsonify({"error": "invalid priority"}), 400
    ticket = Ticket(title=data["title"].strip(), description=data.get("description","").strip(),
                    priority=priority, customer_id=data["customer_id"])
    db.session.add(ticket); db.session.commit()
    ticket.ticket_number = f"TKT-{ticket.id:05d}"; db.session.commit()
    log_activity("Created ticket via API", "Ticket", ticket.id)
    return jsonify(ticket.to_dict()), 201

@app.route("/api/dashboard")
@login_required
def api_dashboard():
    return jsonify({
        "customers": Customer.query.filter_by(active=True).count(),
        "open_tickets": Ticket.query.filter_by(status="Open").count(),
        "in_progress": Ticket.query.filter_by(status="In Progress").count(),
        "resolved": Ticket.query.filter_by(status="Resolved").count(),
        "high_priority_open": Ticket.query.filter(Ticket.priority=="High", Ticket.status!="Resolved").count()
    })

def seed():
    if User.query.count() == 0:
        users = [
            User(name="Admin User", email="admin@example.com", role="Admin",
                 password_hash=generate_password_hash("Admin@123")),
            User(name="Maya Manager", email="manager@example.com", role="Manager",
                 password_hash=generate_password_hash("Manager@123")),
            User(name="Kiran Employee", email="employee@example.com", role="Employee",
                 password_hash=generate_password_hash("Employee@123")),
        ]
        db.session.add_all(users); db.session.commit()
    if Customer.query.count() == 0:
        db.session.add_all([
            Customer(company_name="Aster Manufacturing", contact_person="Ravi Kumar", email="ravi@aster.example", phone="9000000001", industry="Manufacturing"),
            Customer(company_name="Nova Retail Systems", contact_person="Anita Rao", email="anita@nova.example", phone="9000000002", industry="Retail"),
            Customer(company_name="Pacific Logistics", contact_person="Ken Ito", email="ken@pacific.example", phone="9000000003", industry="Logistics"),
        ])
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
