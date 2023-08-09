INSERT INTO organisation ("name") VALUES ('4oh4 Inc.');

INSERT INTO "user" (organisation, "name") VALUES (
     (SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    ,'Callum Inglis'
);

INSERT INTO dice (uuid, "name", faces) VALUES (
	 'TIMECUBE-6716273'
    ,'Clear Dodecahedron'
    ,12
);

INSERT INTO diceface (dice, facenumber) VALUES
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 1),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 2),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 3),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 4),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 5),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 6),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 7),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 8),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 9),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 10),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 11),
    ((SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron'), 12);

INSERT INTO tasktype ("name") VALUES ('Basic Task (No Integration)');

INSERT INTO tasks (tasktype, "name", organisation) VALUES 
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task (No Integration)')
        ,'Building Timer Cube'
        ,(SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    ),
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task (No Integration)')
        ,'AZ-104: Microsoft Azure Administrator (Learning)'
        ,(SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    )
    ,
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task (No Integration)')
        ,'Example Client Feature 2'
        ,(SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    ),
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task (No Integration)')
        ,'Example Client Feature 3'
        ,(SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    ),
    (
        (SELECT tasktypeid FROM tasktype WHERE "name" = 'Basic Task (No Integration)')
        ,'Example Client Feature 1'
        ,(SELECT organisationid FROM organisation WHERE "name" = '4oh4 Inc.')
    )
;

INSERT INTO userdice ("user", dice) VALUES (
     (SELECT userid FROM "user" WHERE "name" = 'Callum Inglis')
    ,(SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron')
);

INSERT INTO dicefacetask (diceface, task) VALUES 
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron') AND "facenumber" = '1')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Building Timer Cube')
    ),
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron') AND "facenumber" = '2')
        ,(SELECT taskid FROM tasks WHERE "name" = 'AZ-104: Microsoft Azure Administrator (Learning)')
    )
    ,
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron') AND "facenumber" = '3')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Example Client Feature 1')
    )
    ,
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron') AND "facenumber" = '4')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Example Client Feature 2')
    ),
    (
        (SELECT dicefaceid FROM diceface WHERE dice = (SELECT diceid FROM dice WHERE "name" = 'Clear Dodecahedron') AND "facenumber" = '5')
        ,(SELECT taskid FROM tasks WHERE "name" = 'Example Client Feature 3')
    )
;

CREATE EXTENSION "uuid-ossp";
INSERT INTO apikey (apikey, "user") VALUES (
    (SELECT uuid_generate_v4()::text), 
    (SELECT userid FROM "user" WHERE "name" = 'Callum Inglis')
);