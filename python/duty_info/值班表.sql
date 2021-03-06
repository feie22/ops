值班表
1.定义人员与电话的字典字典信息：{'张楠':['基础运维服务部', '张楠：18701267230', '张楠：18701267230', '17090140061', '彭兴勃：13146925032'],......}
2.定义人员列表['张楠', '张秋英', ......]
3.定义时间范围 2016-7-4  2016-9-4
4.定义循环周期，每七天循环一个人，总共循环五个人

------------------------------------------------------------
CREATE TABLE `Duty_Info` (
  `ID` INT(11) NOT NULL AUTO_INCREMENT,
  `DUTY_DATE` DATE DEFAULT NULL,
  `DPT` CHAR(20) DEFAULT NULL,
  `DUTY_DAY_IFO` CHAR(30) DEFAULT NULL,
  `DUTY_NIGHT_IFO` CHAR(30) DEFAULT NULL,
  `PUB_PHONE` CHAR(15) DEFAULT NULL,
  `OTHER_PHONE` CHAR(30) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表'
-----------------------------------------------------------

CREATE TABLE `Duty_Base` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(8) DEFAULT NULL,
  `S_DATE` date DEFAULT NULL,
  `E_DATE` date DEFAULT NULL,
  `WEEKS` int(2) DEFAULT NULL,
  `PUB_PHONE` char(15) DEFAULT NULL,
  `OWN_PHONE` char(15) DEFAULT NULL,
  `OTHER_PHONE` char(30) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表-基础运维部' 

CREATE TABLE `Duty_Tool` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(8) DEFAULT NULL,
  `S_DATE` date DEFAULT NULL,
  `E_DATE` date DEFAULT NULL,
  `WEEKS` int(2) DEFAULT NULL,
  `PUB_PHONE` char(15) DEFAULT NULL,
  `OWN_PHONE` char(15) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表-运维工具研发部'

CREATE TABLE `Duty_Data` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DAY_NAME` char(8) DEFAULT NULL,
  `Night_NAME` char(8) DEFAULT NULL,
  `DATE` date DEFAULT NULL,
  `PHONE` char(15) DEFAULT NULL,
  `WEEK` char(6) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表-数据运维服务部'

CREATE TABLE `Duty_Maket` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME1` char(8) DEFAULT NULL,
  `PHONE1` char(15) DEFAULT NULL,
  `NAME2` char(8) DEFAULT NULL,
  `PHONE2` char(15) DEFAULT NULL,
  `S_DATE` date DEFAULT NULL,
  `E_DATE` date DEFAULT NULL,
  `WEEKS` int(2) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表-集市运营组'

CREATE TABLE `Duty_Tool_Soft` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` char(8) DEFAULT NULL,
  `PHONE` char(15) DEFAULT NULL,
  `DATE` date DEFAULT NULL,
   `WEEKS` int(2) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='值班信息表-平台软件运维'