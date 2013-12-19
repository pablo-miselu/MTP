-- Copyright 2013 Pablo De La Garza, Miselu Inc.
-- 
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
-- 
--     http://www.apache.org/licenses/LICENSE-2.0
-- 
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.



CREATE TABLE TestRun
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  SN text,
  siteID text,
  stationID text,
  testSequenceID text,
  startTimestamp timestamp without time zone,
  endTimestamp timestamp without time zone,
  lastTestEntered text,
  isPass boolean,
  CONSTRAINT TestRun_pkey PRIMARY KEY (testRunID)
);

CREATE TABLE TestMeasurement
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  startTimestamp timestamp without time zone,
  endTimestamp timestamp without time zone,
  testName text,
  testMeasurementName text,
  dataType text,
  stringMin text,
  stringMeasurement text,
  stringMax text,
  doubleMin numeric,
  doubleMeasurement numeric,
  doubleMax numeric,
  isPass boolean,
  CONSTRAINT TestMeasurement_pkey PRIMARY KEY (testRunID,testName,testMeasurementName)
);

CREATE TABLE StringDictionary
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  key text,
  value text,
  CONSTRAINT StringDictionary_pkey PRIMARY KEY (testRunID,key)
);

CREATE TABLE DoubleDictionary
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  key text,
  value numeric,
 CONSTRAINT DoubleDictionary_pkey PRIMARY KEY (testRunID,key)
);

CREATE TABLE FileDictionary
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  key text,
  value text,
  CONSTRAINT FileDictionary_pkey PRIMARY KEY (testRunID,key)
);

---   Route Control   ---

CREATE TABLE Transitions
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  SN text,
  processID text,
  nextTestSequenceID text,
  CONSTRAINT Transitions_pkey PRIMARY KEY (creationTimestamp,SN,processID,nextTestSequenceID)
);

CREATE TABLE Components
(
  creationTimestamp timestamp without time zone DEFAULT timezone('UTC'::text, now()),
  testRunID uuid,
  key text,
  value text,
  CONSTRAINT Components_pkey PRIMARY KEY (testRunID,key)
);

