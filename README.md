E-commerce API Project


Requirements / Features:
1. Create a RESTful API with CRUD ops utilizing Flask. 
2. Create models with relationships in MySQL and MySQLAlchemy (one user to many orders, many orders to many products) 
3. Use Marshmallow schemas for input validation
4. Perform testing via Postman to ensure valid endpoints and verify data processes through and is visible on MySQLWorkbench.


To start off, we've got our tables which break down into user, products, orders, and our product / order association. 

To verify via Postman that the endpoints all work, I tested the following endpoints: 

Users - create user, get user list, get user by id, update user, delete user
Products - create product, get product list, get product by id, update product, delete product
Orders - create order, get order list, get order by id, update order, delete product from order


All endpoints were run through Postman to add or modify data to our database, and we confirmed that the data reflects accurately in MySQLWorkbench. 
