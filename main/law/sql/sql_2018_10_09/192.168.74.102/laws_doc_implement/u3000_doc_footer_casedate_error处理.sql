select id,doc_footer,judge_result from implement_civil_etl_v2  
where doc_footer like "%u3000%" or judge_result like "%u3000%" or court_idea like "%u3000%" limit 100;
无结果；

create table casedate_error_uuid_old as 
SELECT * from implement_civil_etl_v2 where SUBSTR(casedate,1,4) > 2018 ;
#无结果

create table casedate_error_uuid_2018 as 
SELECT id,uuid,caseid,casedate from implement_civil_etl_v2 where casedate > "2018-07-27" ;
0

-- SELECT id,uuid,caseid,casedate from implement_civil_etl_v2 where CHAR_LENGTH(casedate) > 1 and CHAR_LENGTH(casedate) < 5 ;
-- 
create  table implement_civil_etl_v2_court_cate_judge_footer like laws_doc_administration.administration_etl_v2_court_cate_judge_footer


create table implement_civil_etl_v2_lawyer_id like laws_doc_adjudication.adjudication_civil_etl_v2_lawyer_id;


create table e as SELECT id ,uuid,type from implement_civil_etl_v2 WHERE id < 5;
create table f as SELECT id ,uuid,type from implement_civil_etl_v2 WHERE id < 5;