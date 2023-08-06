INSERT INTO organisation ("name") VALUES ('Test Organisation');

INSERT INTO "user" (organisation, "name") VALUES (
     (SELECT organisationid FROM organisation WHERE "name" = 'Test Organisation')
    ,'Test User'
);

INSERT INTO dice (uuid, "name", faces) VALUES (
	 'TIMECUBE-6716273'
    ,'Test Dice 1'
    ,12
);

INSERT INTO diceface (dice, facenumber) VALUES
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 1),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 2),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 3),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 4),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 5),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 6),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 7),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 8),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 9),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 10),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 11),
    ((SELECT diceid FROM dice WHERE "name" = 'Test Dice 1'), 12);

INSERT INTO tasktype ("name") VALUES ('Basic Task');

INSERT INTO tasks (tasktype, "name", organisation) VALUES 
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task')
        ,'Test Task 1'
        ,(SELECT organisationid FROM organisation WHERE "name" = 'Test Organisation')
    ),
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task')
        ,'Test Task 2'
        ,(SELECT organisationid FROM organisation WHERE "name" = 'Test Organisation')
    )
    ,
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task')
        ,'Test Task 3'
        ,(SELECT organisationid FROM organisation WHERE "name" = 'Test Organisation')
    ),
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task')
        ,'Test Task 4'
        ,(SELECT organisationid FROM organisation WHERE "name" = 'Test Organisation')
    )
;

INSERT INTO userdice ("user", dice) VALUES (
     (SELECT userid FROM "user" WHERE "name" = 'Test User')
    ,(SELECT diceid FROM dice WHERE "name" = 'Test Dice 1')
);

INSERT INTO dicefacetask (diceface, task) VALUES 
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Test Dice 1') AND "facenumber" = '1')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Test Task 1')
    ),
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Test Dice 1') AND "facenumber" = '2')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Test Task 2')
    )
    ,
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Test Dice 1') AND "facenumber" = '3')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Test Task 3')
    )
    ,
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Test Dice 1') AND "facenumber" = '4')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Test Task 4')
    )
;

CREATE EXTENSION "uuid-ossp";
INSERT INTO apikey (apikey, "user") VALUES (
    (SELECT uuid_generate_v4()::text), 
    (SELECT userid FROM "user" WHERE "name" = 'Test User')
);