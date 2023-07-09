import sqlite3
import mysql.connector
import pandas as pd


def embedded_sql_queries(cursor):

    print("Select the Query you want to execute.")
    print("1. Find the name of the customers who have ordered any cloth of color blue")
    print("2. Find uid,name,email of user who has max orders")

    choice = int(input("Enter your choice "))

    query1 = ''' select fname, lname from Customer
                where uid in (
                    select uid
                    from Corders
                    where cordid in (
                        select cordid
                        from Cart
                        where pdid in (
                            select Products.pdid
                            from Products, Clothes
                            where Clothes.pdid = Products.pdid and Clothes.color = 'blue'
                        )
                    )
                );'''

    query2 = ''' SELECT uid,fname,lname,email
                from Customer
                Where uid in(
                    select uid 
                    from Corders
                    group by uid
                    having count(*) = (
                        SELECT max(order_count) FROM(
                            SELECT COUNT(*) as order_count
                            from Corders
                            group by uid
                        ) AS order_counts
                    )
                );'''
    data = None
    if choice == 1:

        cursor.execute(query1)
        data = cursor.fetchall()

    else:
        cursor.execute(query2)
        data = cursor.fetchall()

    for d in data:
        print(d)


def olap_queries(cursor):
    print("OLAP Queries.")
    print("1. Query to calculate the total sales for each city and gender and display them in the result set")

    query1 = '''SELECT city, gender, SUM(totalCost) as sales 
            FROM Customer 
            INNER JOIN Corders ON Customer.uid = Corders.uid 
            GROUP BY city, gender WITH ROLLUP;'''

    print("2. Find the total sales in each category.")
    query2 = '''SELECT Category.catname, SUM(Corders.totalCost) as total_sales
                FROM Corders
                INNER JOIN Cart ON Corders.cordid = Cart.ordid
                INNER JOIN Products ON Cart.pdid = Products.pdid
                INNER JOIN Category ON Products.catid = Category.catid
                GROUP BY Category.catname WITH ROLLUP;'''

    print("3.Find total revenue by month and category, with subtotals for each month and category, and a grand total:")
    query3 = ''' SELECT YEAR(dateoforderplaced) AS Year, MONTH(dateoforderplaced) AS Month, Category.catname, SUM(sellingPrice * quantity * (100 - 10) / 100) AS TotalRevenue 
                FROM Corders 
                JOIN Cart ON Corders.cordid = Cart.ordid 
                JOIN Products ON Cart.pdid = Products.pdid 
                JOIN Category ON Products.catid = Category.catid 
                GROUP BY YEAR(dateoforderplaced), MONTH(dateoforderplaced), Category.catname WITH ROLLUP;'''

    print("4.Valuation of products of each brand acorss categories")
    query4 = ''' select catid, brand, sum(costPrice) as productsValue
                from products
                group by catid, brand with rollup;'''

    print("5.Find the total sales of each product category for each year, including the grand total:")
    query5 = '''SELECT YEAR(dateoforderplaced) AS year, catname, SUM(subtotal) AS total_sales
                FROM Corders
                INNER JOIN Cart ON Corders.cordid = Cart.ordid
                INNER JOIN Products ON Cart.pdid = Products.pdid
                INNER JOIN Category ON Products.catid = Category.catid
                GROUP BY year, catname WITH ROLLUP;'''

    choice = int(input("Enter your choice. "))
    if choice == 1:
        cursor.execute(query1)
    elif choice == 2:
        cursor.execute(query2)
    elif choice == 3:
        cursor.execute(query3)
    elif choice == 4:
        cursor.execute(query4)
    else:
        cursor.execute(query5)

    data = cursor.fetchall()

    for d in data:
        print(d)


def triggers(conn, cursor):
    trigger_query1 = '''create  trigger doDiscount
            before insert on Products
            for each row
            set new.discount=new.costPrice*0.1,
            new.sellingPrice=new.costPrice-new.discount;'''

    trigger_query2 = '''create  trigger discountDu
            before update on Products
            for each row
            set new.discount=new.costPrice*0.1,
            new.sellingPrice=new.costPrice-new.discount;'''

    cursor.execute("DROP TRIGGER IF EXISTS doDiscount;")
    cursor.execute("DROP TRIGGER IF EXISTS discountDu;")

    cursor.execute(trigger_query1)
    cursor.execute(trigger_query2)

    print("Showing Triggers for Insertion \n")
    print("Inserting  a product with pdid = 301 and Cost Price = 10000, Discount = 0 and Selling Price = 0 ")
    print("Running the query now to insert the values.\n")
    cursor.execute("INSERT INTO Products VALUES (301,3,'Built-in DishCleaner 101','Whirlpool','https://Built-in DishCleaner 101.pl/350x200/ff0000/000','Built-in DishWasher101',10000,0,0,5);")
    print("Details stored in the database.")
    cursor.execute("select * from Products where pdid = 301")
    data = cursor.fetchall()
    print(data)
    print()
    print("Showing trigger for Updation.")
    print("Updating the Cost Price of above item to 15000.\n")
    update_query = "update Products set costPrice = 15000 where pdid = 301"
    cursor.execute(update_query)
    cursor.execute("select * from Products where pdid = 301")
    data = cursor.fetchall()
    print("New Details of the product: ")
    print(data)


def menu():
    conn = mysql.connector.connect(host="localhost", user="root", password="qwertyuiop", database='dbms_project')
    cursor = conn.cursor()
    while True:
        print("Select choice from the menu below: ")
        print("1. Embedded SQL Queries. ")
        print("2. OLAP Queries")
        print("3. Triggers. ")
        print("4. Exit.")

        choice = int(input("Enter your choice."))

        if choice == 1:
            embedded_sql_queries(cursor)
        elif choice == 2:
            olap_queries(cursor)
        elif choice == 3:
            triggers(conn, cursor)
        else:
            break


if __name__ == '__main__':
    menu()