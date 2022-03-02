PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Project" (
	id INTEGER NOT NULL, 
	name TEXT NOT NULL, 
	date_created DATETIME NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO Project VALUES(1,'Online Store','2022-03-02 02:15:56.135208');
CREATE TABLE IF NOT EXISTS "TestProcedure" (
	id INTEGER NOT NULL, 
	project_id INTEGER, 
	name TEXT NOT NULL, 
	date_created DATETIME NOT NULL, 
	approval BOOLEAN NOT NULL, 
	notes TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES "Project" (id)
);
INSERT INTO TestProcedure VALUES(1,1,'Login','2022-03-02 02:16:23.139865',1,'Ensure Login Works');
INSERT INTO TestProcedure VALUES(2,1,'Registration','2022-03-02 02:16:32.321084',1,'');
INSERT INTO TestProcedure VALUES(3,1,'Purchasing','2022-03-02 02:16:43.905614',0,'');
CREATE TABLE IF NOT EXISTS "TestStep" (
	id INTEGER NOT NULL, 
	name TEXT NOT NULL, 
	instructions TEXT NOT NULL, 
	pass_condition TEXT NOT NULL, 
	status INTEGER NOT NULL, 
	procedure_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(procedure_id) REFERENCES "TestProcedure" (id)
);
INSERT INTO TestStep VALUES(1,'Accept Valid Credentials','Navigate to the login page, enter valid credentials, and click login.','The login should succeed',0,1);
INSERT INTO TestStep VALUES(2,'Reject Invalid Credentials','Navigate to the login page. Enter Invalid Credentials. Click login.','The login should fail with an error message',0,1);
INSERT INTO TestStep VALUES(3,'Blacklist after repeated login attempts.','Navigate to the login page. Attempt to login with invalid credentials 5 times within 2 minutes.','The system should prevent any more login attempts from that user, and notify the user they have made too many login attempts',0,1);
INSERT INTO TestStep VALUES(4,'Accepts Valid Credentials','Navigate to the registration page, enter valid information, click register. Then attempt to login with the provided credentials.','The registration and login should succeed',0,2);
INSERT INTO TestStep VALUES(5,'Reject Duplicate Email','Navigate to the registration page, attempt to register with an email already in the system. Then attempt to login with the provided credentials.','The registration and login should fail, with an error message notifying the user that the email is already registered.',0,2);
INSERT INTO TestStep VALUES(6,'Adding Products to Cart','Navigate to the store page. Add 5 items to your cart. Then hit "view cart".','The "view cart" page should show all items added, along with the subtotal.',0,3);
INSERT INTO TestStep VALUES(7,'Accept valid payment','Navigate to the shop page. Add 5 items to cart. Click checkout. Attempt to checkout with a valid credit card.','The checkout should succeed and show the order reciept.',0,3);
INSERT INTO TestStep VALUES(8,'Reject invalid payment','Navigate to the shop page. Add 5 items to cart. Click checkout. Attempt to checkout with an invalid credit card.','The system notifies the user that the payment method is not valid',0,3);
COMMIT;
