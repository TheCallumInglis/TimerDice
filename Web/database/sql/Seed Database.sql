INSERT INTO "Organisation" ("Name") VALUES ('Test Organisation');

INSERT INTO "User" ("Organisation", "Name") VALUES (
     (SELECT "OrganisationID" FROM "Organisation" WHERE "Name" = 'Test Organisation')
    ,'Test User'
);

INSERT INTO "Dice" ("UUID", "Name", "Faces") VALUES (
	 'TIMECUBE-6716273'
    ,'Test Dice 1'
    ,6
);

INSERT INTO "DiceFace" ("Dice", "FaceNumber") VALUES
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 1),
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 2),
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 3),
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 4),
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 5),
    ((SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1'), 6);

INSERT INTO "TaskType" ("Name") VALUES ('Basic Task');

INSERT INTO "Tasks" ("TaskType", "Name", "Organisation") VALUES (
     (SELECT "TaskTypeID" FROM "TaskType" WHERE "Name" = 'Basic Task')
    ,'Test Task 1'
    ,(SELECT "OrganisationID" FROM "Organisation" WHERE "Name" = 'Test Organisation')
);

INSERT INTO "UserDice" ("User", "Dice") VALUES (
     (SELECT "UserID" FROM "User" WHERE "Name" = 'Test User')
    ,(SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1')
);

INSERT INTO "DiceFaceTask" ("DiceFace", "Task") VALUES (
     (SELECT "DiceFaceID" FROM "DiceFace" WHERE "Dice" = (SELECT "DiceID" FROM "Dice" WHERE "Name" = 'Test Dice 1') AND "FaceNumber" = '1')
    ,(SELECT "TaskID" FROM "Tasks" WHERE "Name" = 'Test Task 1')
);

CREATE EXTENSION "uuid-ossp";
INSERT INTO "APIKEY" ("APIKEY", "USER") VALUES (
    (SELECT uuid_generate_v4()::text;), (SELECT "UserID" FROM "USER" WHERE "NAME" = 'Test User')
);