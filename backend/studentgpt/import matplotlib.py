import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create a figure
fig, ax = plt.subplots(figsize=(10, 6))

# Function to draw entity
def entity(x, y, text):
    rect = mpatches.Rectangle((x, y), 2.5, 1, edgecolor="black", facecolor="lightblue")
    ax.add_patch(rect)
    ax.text(x+1.25, y+0.5, text, ha="center", va="center", fontsize=10, weight="bold")
    return rect

# Function to draw relationship (diamond)
def relationship(x, y, text):
    diamond = mpatches.RegularPolygon((x, y), numVertices=4, radius=0.7, orientation=0.785,
                                      edgecolor="black", facecolor="lightyellow")
    ax.add_patch(diamond)
    ax.text(x, y, text, ha="center", va="center", fontsize=9)
    return diamond

# Draw entities
branch = entity(0, 4, "Branch\n(Branch_ID)")
account = entity(6, 5.5, "Account\n(Account_No)")
customer = entity(6, 2.5, "Customer\n(Customer_ID)")
loan = entity(12, 4, "Loan\n(Loan_No)")

# Draw relationships
branch_account = relationship(3, 5, "Has")
branch_loan = relationship(9, 5, "Sanctions")
cust_account = relationship(6, 4, "Holds")
cust_loan = relationship(9, 3, "Borrows")

# Draw lines between entities and relationships
def connect(x1, y1, x2, y2, text=""):
    ax.plot([x1, x2], [y1, y2], color="black")
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2, text, fontsize=8, ha="center", va="center")

# Connections with cardinalities
connect(2.5, 4.5, 2.3, 5, "1")
connect(3.7, 5, 6, 5.75, "M")

connect(2.5, 4.5, 2.3, 5, "")

connect(7.5, 5.75, 8.3, 5, "M")
connect(9.7, 5, 12, 4.5, "1")

connect(6, 5, 6, 4.5, "M")
connect(6, 3.5, 6, 4, "N")

connect(7.5, 2.75, 8.3, 3, "M")
connect(9.7, 3, 12, 4.5, "N")

# Adjust plot
ax.set_xlim(-1, 14)
ax.set_ylim(1, 7)
ax.axis("off")

plt.title("ER Diagram for Banking System (Chen Notation)", fontsize=12, weight="bold")
plt.show()
