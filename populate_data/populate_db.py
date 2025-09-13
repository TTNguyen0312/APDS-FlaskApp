import pandas as pd
import sqlite3


df = pd.read_csv("assignment3_II.csv")


df.columns = df.columns.str.strip()


conn = sqlite3.connect("sdms.db")
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS Clothes;")
cursor.execute("DROP TABLE IF EXISTS Reviews;")


cursor.execute("""
CREATE TABLE Clothes (
    ClothingID INTEGER PRIMARY KEY,
    ClothTitle TEXT NOT NULL,
    ClothDescription TEXT,
    Department TEXT,
    ClassName TEXT,
    DivisionName TEXT
);
""")

# Reviews Table
cursor.execute("""
CREATE TABLE Reviews (
    ReviewID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClothingID INTEGER,
    Age INTEGER,
    ReviewTitle TEXT,
    ReviewText TEXT,
    Rating INTEGER,
    Recommended INTEGER,
    PositiveFeedbackCount INTEGER,
    FOREIGN KEY (ClothingID) REFERENCES Clothes(ClothingID)
);
""")


clothes_df = df.drop_duplicates(subset=["Clothing ID"])[
    ["Clothing ID", "Clothes Title", "Clothes Description",
     "Department Name", "Class Name", "Division Name"]
]

# insert into Clothes
for _, row in clothes_df.iterrows():
    cursor.execute("""
        INSERT INTO Clothes (ClothingID, ClothTitle, ClothDescription, Department, ClassName, DivisionName)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["Clothing ID"],
        row["Clothes Title"],
        row["Clothes Description"],
        row["Department Name"],
        row["Class Name"],
        row["Division Name"]
    ))

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Reviews (ClothingID, Age, ReviewTitle, ReviewText, Rating, Recommended, PositiveFeedbackCount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Clothing ID"],
        row["Age"],
        row["Title"],
        row["Review Text"],
        row["Rating"],
        row["Recommended IND"],
        row["Positive Feedback Count"]
    ))

# Save (commit) the changes and close the connection
conn.commit()
conn.close()

print("Database created successfully: sdms.db")


conn = sqlite3.connect("sdms.db")
cursor = conn.cursor()

print("Sample Clothes row:", cursor.execute("SELECT * FROM Clothes LIMIT 1;").fetchone())
print("Sample Review row:", cursor.execute("SELECT * FROM Reviews LIMIT 1;").fetchone())

conn.close()
