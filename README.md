Task : ERP User & Role Management
Task 1 (Backend - Django)
Scenario:
In an ERP system, different users (Admin, Manager, Employee) have different levels of access. You need to implement an authentication and role-based access control (RBAC) system.
Requirements:
1.	Create a Django REST Framework (DRF) API for user authentication (Login, Logout, JWT-based authentication).
2.	Implement role-based access control (RBAC) where: 
o	Admins can create, update, delete users.
o	Managers can view all employees but cannot edit Admins.
o	Employees can only view their own profile.
3.	Design a PostgreSQL/MySQL database schema for storing user roles.
4.	Implement API endpoints: 
o	POST /register - Register a new user.
o	POST /login - Authenticate and return JWT token.
o	GET /users - List users (only for Admin & Manager).
o	GET /profile - View own profile (for all users).
5.	Implement proper permissions and authentication in DRF.
