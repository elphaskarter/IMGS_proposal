      PROGRAM MOLBMP

!     THIS ROUTINE MAKES CONVERSIONS BETWEEN ASCII AND DIRECT-ACCESS
!     BINARY MODTRAN4 MOLECULAR BAND MODEL PARAMETER FILES.
!     THE DATA IS CALCULATED FROM THE HITRAN96 LINE COMPILATION.

!     DECLARE VARIABLES, ARRAYS AND FUNCTIONS
      INTEGER MXTEMP
      PARAMETER(MXTEMP=11)
      CHARACTER ANSWER*1,ASCNAM*150,BINNAM*150,                         &
     &  ACCESS*12,MESSAG*7,HEADER*48
      LOGICAL LEXIST
      INTEGER IBNDWD,NTEMP,IT,J,IASCII,IBNARY,NDIVID,NREC,LENASC,       &
     &  LENBIN,IRECLN,MXRCLN,IBIN,IALF,IMOL,IF1ST,IFLAST,LSTREC
      REAL DEDGE,DEDGEB,TBAND(MXTEMP),SD(MXTEMP),OD(MXTEMP)

!     FOR COMPARING BINARY AND ASCII FILES
      REAL SDASC(MXTEMP,3),ODASC(MXTEMP,3),SDBIN(MXTEMP,3),             &
     &  ODBIN(MXTEMP,3),TBANDB(MXTEMP)
      INTEGER IWDBIN,NTEMPB,IF1STB,IFLASB,NDIVDB,LSTRCB
      INTEGER IBINB(3),IALFB(3),IMOLB(3),IBINA(3),IALFA(3),IMOLA(3)
      INTEGER MINLEN,IOS

!     LIST DATA
      DATA IASCII/9/,IBNARY/10/

!     SELECT ACTION
      WRITE(*,'(/2A,/(17X,A))')' PROGRAM MOLBMP: ',                     &
     &     ' CONVERTS BETWEEN THE SEQUENTIAL-ACCESS ASCII',             &
     &     ' (FORMATTED) AND THE DIRECT-ACCESS BINARY (UNFORMATTED)',   &
     &     ' MODTRAN4 MOLECULAR BAND MODEL PARAMETER FILES',            &
     &     ' (THE FILE FROM WHICH DATA IS READ IS NOT DELETED).'
   10 CONTINUE
      WRITE(*,'(/(2A))')' ENTER  1   TO CREATE BINARY (UNFORMATTED)',   &
     &     ' FILE FROM ASCII (FORMATTED) FILE','        2   TO CREATE', &
     &     ' ASCII (FORMATTED) FILE FROM BINARY (UNFORMATTED) FILE'
      READ(*,'(A1)',END=10,ERR=10)ANSWER
      IF(ANSWER.EQ.'1')THEN

!         ENTER NAME AND OPEN OLD ASCII FILE
   20     CONTINUE
          WRITE(*,'(/(A))')
     &      ' ENTER ASCII BAND MODEL FILE NAME (MAX 150 CHARACTERS)',   &
     &      '      [ENTER 0 FOR NAME = "B2001_01.ASC"]',                &
     &      '      [ENTER 1 FOR NAME = "B2001_05.ASC"]',                &
     &      '      [ENTER 2 FOR NAME = "B2001_15.ASC"]'
          READ(*,'(A)',END=20,ERR=20)ASCNAM
          LENASC=MINLEN(ASCNAM)
          IF(LENASC.EQ.0)GOTO 20
          IF(LENASC.EQ.1)THEN

!             CHECK FOR DEFAULT NAMES.
              IF(ASCNAM(1:1).EQ.'0')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_01.ASC'
              ELSEIF(ASCNAM(1:1).EQ.'1')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_05.ASC'
              ELSEIF(ASCNAM(1:1).EQ.'2')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_15.ASC'
              ENDIF
          ENDIF
          INQUIRE(FILE=ASCNAM(1:LENASC),EXIST=LEXIST)
          IF(.NOT.LEXIST)THEN
              WRITE(*,'(/3A)')' FILE "',ASCNAM(1:LENASC),               &
     &          '" DOES NOT EXIST.  PLEASE RE-ENTER.'
              GOTO 20
          ENDIF
          OPEN(IASCII,FILE=ASCNAM(1:LENASC),STATUS='OLD')

!         READ THE NUMBER OF TEMPERATURES (NTEMP) FROM HEADER.
          MESSAG=' HEADER'
          READ(IASCII,'(I3)',END=80,ERR=80)NTEMP
          IF(NTEMP.LE.0 .OR. NTEMP.GT.MXTEMP)THEN
              WRITE(*,'(/2A,I3,A,/8X,2A,I3,A)')                         &
     &          ' ERROR:  INPUT NUMBER OF TEMPERATURES',                &
     &          ' (NTEMP =',NTEMP,' MUST BE',' POSITIVE AND',           &
     &          ' CAN NOT EXCEED PARAMETER MXTEMP (=',MXTEMP,').'
              STOP 'NTEMP OUT OF RANGE'
          ENDIF
          REWIND(IASCII)

!         SET INITIAL AND MAXIMUM RECORD LENGTH
!         INTEGER AND REAL VARIABLES ON HP ARE OF RECORD LENGTH 4
!         ON IBM VM/CMS, IT IS 4; THERE IS ALSO A 4 BYTE PADDING
!         INTEGER AND REAL VARIABLES ON SGI & DEC ARE OF RECORD LENGTH 1
          IRECLN=2*NTEMP+3
          MXRCLN=4*IRECLN+4

!         ENTER NAME AND OPEN NEW BINARY FILE
   30     CONTINUE
          WRITE(*,'(/(A))')                                             &
     &      ' ENTER BINARY BAND MODEL FILE NAME (MAX 150 CHARACTERS)',  &
     &      '      [ENTER 0 FOR NAME = "B2001_01.BIN"]',                &
     &      '      [ENTER 1 FOR NAME = "B2001_05.BIN"]',                &
     &      '      [ENTER 2 FOR NAME = "B2001_15.BIN"]'
          READ(*,'(A)',END=30,ERR=30)BINNAM
          LENBIN=MINLEN(BINNAM)
          IF(LENBIN.EQ.0)GOTO 30
          IF(LENBIN.EQ.1)THEN
              IF(BINNAM(1:1).EQ.'0')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_01.BIN'
              ELSEIF(BINNAM(1:1).EQ.'1')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_05.BIN'
              ELSEIF(BINNAM(1:1).EQ.'2')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_15.BIN'
              ENDIF
          ENDIF
          INQUIRE(FILE=BINNAM(1:LENBIN),EXIST=LEXIST)
          IF(LEXIST)THEN
              WRITE(*,'(/4A,/11X,A)')' WARNING:  ',                     &
     &          'THE FILE "',BINNAM(1:LENBIN),'" ALREADY EXISTS.',      &
     &          'DO YOU WISH TO OVERWRITE THE PRE-EXISTING FILE (Y/N)?'
              READ(*,'(A1)')ANSWER
              IF(ANSWER.NE.'Y' .AND. ANSWER.NE.'y')GOTO 30
              OPEN(IBNARY,FILE=BINNAM(1:LENBIN),STATUS='OLD')
              CLOSE(IBNARY,STATUS='DELETE')
          ENDIF
   40     CONTINUE
          OPEN(IBNARY,FILE=BINNAM(1:LENBIN),STATUS='NEW',               &
     &      FORM='UNFORMATTED',ACCESS='DIRECT',RECL=IRECLN)

!         READ THE BAND MODEL FILE HEADER:
!           IBNDWD   BIN WIDTH [CM-1].
!           IF1ST    BEGINNING FREQUENCY [CM-1].
!           IFLAST   FINAL FREQUENCY [CM-1].
!           LSTREC   RECORD NUMBER OF FINAL RECORD.
!           DEDGE    DISTANCE FROM BIN EDGE TO LINE CENTER [CM-1].
          MESSAG=' HEADER'
          READ(IASCII,*,END=80,ERR=80)NTEMP,(TBAND(IT),IT=1,NTEMP)
          READ(IASCII,'(A48)')HEADER
          READ(HEADER,'(5I8,F8.3)',IOSTAT=IOS)                          &
     &      IBNDWD,IF1ST,IFLAST,LSTREC,NDIVID,DEDGE
          IF(IOS.NE.0)THEN

!             OLD FORMAT:
              READ(HEADER(1:40),'(4I8,F8.3)')                           &
     &          IBNDWD,IF1ST,IFLAST,LSTREC,DEDGE
              NDIVID=1
          ENDIF

!         WRITE THE MOLECULAR BAND MODEL PARAMETER HEADER TO BINARY FILE
          NREC=1
          WRITE(IBNARY,REC=NREC,ERR=70)NTEMP,(TBAND(IT),IT=1,NTEMP),    &
     &      IBNDWD,IF1ST,IFLAST,LSTREC,NDIVID,DEDGE

!         ECHO HEADER INFO
          WRITE(*,'(/5X,A,/I3,0P11F7.0)')                               &
     &      'NTEMP,(TBAND(IT),IT=1,NTEMP)',NTEMP,(TBAND(IT),IT=1,NTEMP)
          WRITE(*,'(/2(A,I7,5X),A,I7,/2(A,I7,5X),A,F7.3)')              &
     &      'IBNDWD=',IBNDWD,' IF1ST=', IF1ST,'IFLAST=',IFLAST,         &
     &      'LSTREC=',LSTREC,'NDIVID=',NDIVID,' DEDGE=', DEDGE

!         READ AND WRITE BAND MODEL DATA - ONE LINE OR ONE RECORD AT
!         A TIME.  A "LINE" OR A "RECORD" CONSISTS OF:  IBIN, IMOL,
!         SD(1), ..., SD(NTEMP), IALF, ..., OD(1), ..., OD(NTEMP).
          MESSAG='  DATA '
   50     CONTINUE
          READ(IASCII,*,END=60,ERR=80)                                  &
     &      IBIN,IMOL,(SD(IT),IT=1,NTEMP),IALF,(OD(IT),IT=1,NTEMP)
          NREC=NREC+1
          WRITE(IBNARY,REC=NREC,ERR=70)                                 &
     &      IBIN,IMOL,(SD(IT),IT=1,NTEMP),IALF,(OD(IT),IT=1,NTEMP)

!         SAVE THE FIRST 2 AND THE LAST BAND MODEL RECORDS FOR TESTING
          IF(NREC.LE.3)THEN
              IBINA(NREC-1)=IBIN
              IMOLA(NREC-1)=IMOL
              IALFA(NREC-1)=IALF
              DO IT=1,NTEMP
                  SDASC(IT,NREC-1)=SD(IT)
                  ODASC(IT,NREC-1)=OD(IT)
              ENDDO
              IF(NREC.EQ.2)                                             &
     &          WRITE(*,'(/A)')' THE FIRST TWO BAND MODEL RECORDS ARE:'
              WRITE(*,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
              WRITE(*,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)
          ENDIF
          IF(8000*(NREC/8000).EQ.NREC)THEN

!             WRITE EACH 8000 RECORDS TO KEEP USER AWARE OF PROGRESS.
              WRITE(*,'(/A,I7,A)')' BAND MODEL RECORD',NREC,' IS:'
              WRITE(*,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
              WRITE(*,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)
          ENDIF
          GOTO 50
   60     CONTINUE

!         SAVE LAST RECORD FOR TESTING.
          IBINA(3)=IBIN
          IMOLA(3)=IMOL
          IALFA(3)=IALF
          DO IT=1,NTEMP
              SDASC(IT,3)=SD(IT)
              ODASC(IT,3)=OD(IT)
          ENDDO
          WRITE(*,'(/A,I7,A)')'THE LAST RECORD, ',NREC,', IS:'
          WRITE(*,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
          WRITE(*,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)

!         TEST BINARY FILE
          CLOSE(IBNARY,STATUS='KEEP')
          WRITE(*,'(/A)')' TESTING BINARY TAPE'
          OPEN(IBNARY,FILE=BINNAM(1:LENBIN),STATUS='OLD',               &
     &      FORM='UNFORMATTED',ACCESS='DIRECT',RECL=IRECLN)

          READ(IBNARY,REC=1,ERR=70)NTEMPB,(TBANDB(IT),IT=1,NTEMP),      &
     &      IWDBIN,IF1STB,IFLASB,LSTRCB,NDIVDB,DEDGEB
          IF(NTEMPB.NE.NTEMP .OR. IWDBIN.NE.IBNDWD .OR. IF1STB.NE.IF1ST &
     &      .OR. IFLASB.NE.IFLAST .OR. NDIVDB.NE.NDIVID                 &
     &      .OR. LSTRCB.NE.LSTREC .OR. DEDGEB.NE.DEDGE)GOTO 70
          DO IT=1,NTEMP
              IF(TBANDB(IT).NE.TBAND(IT))GOTO 70
          ENDDO
          READ(IBNARY,REC=2,ERR=70)IBINB(1),IMOLB(1),                   &
     &      (SDBIN(IT,1),IT=1,NTEMP),IALFB(1),                          &
     &      (ODBIN(IT,1),IT=1,NTEMP)
          READ(IBNARY,REC=3,ERR=70)IBINB(2),IMOLB(2),                   &
     &      (SDBIN(IT,2),IT=1,NTEMP),IALFB(2),                          &
     &      (ODBIN(IT,2),IT=1,NTEMP)
          READ(IBNARY,REC=NREC,ERR=70)IBINB(3),IMOLB(3),                &
     &      (SDBIN(IT,3),IT=1,NTEMP),IALFB(3),                          &
     &      (ODBIN(IT,3),IT=1,NTEMP)
          DO J=1,3
              IF(IBINA(J).NE.IBINB(J))GOTO 70
              IF(IMOLA(J).NE.IMOLB(J))GOTO 70
              IF(IALFA(J).NE.IALFB(J))GOTO 70
              DO IT=1,NTEMP
                  IF(SDASC(IT,J).NE.SDBIN(IT,J))GOTO 70
                  IF(ODASC(IT,J).NE.ODBIN(IT,J))GOTO 70
              ENDDO
          ENDDO

!         SUCCESSFUL WRITE
          WRITE(*,'(/A,I7,A,I6,A)')                                     &
     &      ' BAND MODEL PARAMETER FILE CONTAINS',NREC,                 &
     &      ' RECORDS (LAST FREQUENCY IS',IFLAST,' CM-1)'
          CLOSE(IASCII,STATUS='KEEP')
          CLOSE(IBNARY,STATUS='KEEP')
          WRITE(*,'(/3A,/5X,A)')' SUCCESSFULLY CREATED',                &
     &      ' THE DIRECT-ACCESS, BINARY (UNFORMATTED)',                 &
     &      ' BAND MODEL FILE:',BINNAM(1:LENBIN)
          STOP 'Success!'

!         INCREASE RECORD LENGTH AND START OVER
   70     CONTINUE
          CLOSE(IBNARY,STATUS='DELETE')
          IF(IRECLN.GE.MXRCLN)THEN
              WRITE(*,'(/3A,/A,I8)')' ERROR:  UNABLE TO WRITE',         &
     &          ' DIRECT-ACCESS BINARY FILE:  ',BINNAM(1:LENBIN),       &
     &          '         LARGEST RECORD LENGTH TRIED WAS',IRECLN
              STOP
          ENDIF
          WRITE(*,FMT='(/(2A,I8,A))')' AN ERROR OCCURRED',              &
     &      ' WHEN A RECORD LENGTH OF',IRECLN,' WAS USED.'
          IF(IRECLN.EQ.MXRCLN-4)THEN
              IRECLN=MXRCLN
          ELSE
              IRECLN=2*IRECLN
          ENDIF
          WRITE(*,FMT='((A,I8,A))')                                     &
     &      ' A RECORD LENGTH OF',IRECLN,' WILL NOW BE TRIED.'
          REWIND(IASCII)
          GOTO 40

!         UNABLE TO READ ASCII FILE
   80     CONTINUE
          IF(LENASC.GT.0)WRITE(*,'(/(5A))')' ERROR:  UNABLE',           &
     &      ' TO READ',MESSAG,' FROM ASCII FILE:  ',ASCNAM(1:LENASC),   &
     &      '         NO BINARY FILE WAS CREATED.'
          CLOSE(IASCII,STATUS='KEEP')
          CLOSE(IBNARY,STATUS='DELETE')
          STOP
      ELSEIF(ANSWER.EQ.'2')THEN

!         ENTER NAME OF OLD BINARY FILE
   90     CONTINUE
          WRITE(*,'(/2A,/(A))')' ENTER NAME OF BINARY',                 &
     &      ' BAND MODEL FILE (MAX 150 CHARACTERS)',                    &
     &      '      [ENTER 0 FOR NAME = "B2001_01.BIN"]',                &
     &      '      [ENTER 1 FOR NAME = "B2001_05.BIN"]',                &
     &      '      [ENTER 2 FOR NAME = "B2001_15.BIN"]'
          READ(*,'(A)',END=90,ERR=90)BINNAM
          LENBIN=MINLEN(BINNAM)
          IF(LENBIN.EQ.0)GOTO 90
          IF(LENBIN.EQ.1)THEN
              IF(BINNAM(1:1).EQ.'0')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_01.BIN'
              ELSEIF(BINNAM(1:1).EQ.'1')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_05.BIN'
              ELSEIF(BINNAM(1:1).EQ.'2')THEN
                  LENBIN=12
                  BINNAM(1:LENBIN)='B2001_15.BIN'
              ENDIF
          ENDIF
!         INQUIRE(FILE=BINNAM(1:LENBIN),EXIST=LEXIST,DIRECT=ACCESS)
          INQUIRE(FILE=BINNAM(1:LENBIN),EXIST=LEXIST)
          IF(.NOT.LEXIST)THEN
              WRITE(*,'(/3A)')' FILE "',BINNAM(1:LENBIN),               &
     &          '" DOES NOT EXIST.  PLEASE RE-ENTER.'
              GOTO 90
          ENDIF

!         READ THE NUMBER OF TEMPERATURES (NTEMP) FROM HEADER.
          IRECLN=8
          OPEN(IBNARY,FILE=BINNAM(1:LENBIN),STATUS='OLD',               &
     &      FORM='UNFORMATTED',ACCESS='DIRECT',RECL=IRECLN,ERR=150)
          NREC=1
          MESSAG=' HEADER'
          READ(IBNARY,REC=NREC,ERR=150)NTEMP
          CLOSE(IBNARY,STATUS='KEEP')
          IF(NTEMP.LE.0 .OR. NTEMP.GT.MXTEMP)THEN
              WRITE(*,'(/2A,I3,A,/8X,2A,I3,A)')                         &
     &          ' ERROR:  INPUT NUMBER OF TEMPERATURES',                &
     &          ' (NTEMP =',NTEMP,' MUST BE',' POSITIVE AND',           &
     &          ' CAN NOT EXCEED PARAMETER MXTEMP (=',MXTEMP,').'
              STOP 'NTEMP OUT OF RANGE'
          ENDIF

!         SET INITIAL AND MAXIMUM RECORD LENGTH
!         INTEGER AND REAL VARIABLES ON HP ARE OF RECORD LENGTH 4
!         ON IBM VM/CMS, IT IS 4; THERE IS ALSO A 4 BYTE PADDING
!         INTEGER AND REAL VARIABLES ON SG & DEC ARE OF RECORD LENGTH 1
          IRECLN=2*NTEMP+3
          MXRCLN=4*IRECLN+4

!         ENTER NAME OF NEW ASCII FILE
  100     CONTINUE
          WRITE(*,'(/(A))')                                             &
     &      ' ENTER ASCII BAND MODEL FILE NAME (MAX 150 CHARACTERS)',   &
     &      '      [ENTER 0 FOR NAME = "B2001_01.ASC"]',                &
     &      '      [ENTER 1 FOR NAME = "B2001_05.ASC"]',                &
     &      '      [ENTER 2 FOR NAME = "B2001_15.ASC"]'
          READ(*,'(A)',END=100,ERR=100)ASCNAM
          LENASC=MINLEN(ASCNAM)
          IF(LENASC.EQ.0)GOTO 100
          IF(LENASC.EQ.1)THEN
              IF(ASCNAM(1:1).EQ.'0')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_01.ASC'
              ELSEIF(ASCNAM(1:1).EQ.'1')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_05.ASC'
              ELSEIF(ASCNAM(1:1).EQ.'2')THEN
                  LENASC=12
                  ASCNAM(1:LENASC)='B2001_15.ASC'
              ENDIF
          ENDIF
          INQUIRE(FILE=ASCNAM(1:LENASC),EXIST=LEXIST)
          IF(LEXIST)THEN
              WRITE(*,'(/4A,/11X,A)')' WARNING:  ',                     &
     &          'THE FILE "',ASCNAM(1:LENASC),'" ALREADY EXISTS.',      &
     &          'DO YOU WISH TO OVERWRITE THE PRE-EXISTING FILE (Y/N)?'
              READ(*,'(A1)')ANSWER
              IF(ANSWER.NE.'Y' .AND. ANSWER.NE.'y')GOTO 100
              OPEN(IASCII,FILE=ASCNAM(1:LENASC),STATUS='OLD')
              CLOSE(IASCII,STATUS='DELETE')
          ENDIF
  110     CONTINUE
          OPEN(IASCII,FILE=ASCNAM(1:LENASC),STATUS='NEW')
          OPEN(IBNARY,FILE=BINNAM(1:LENBIN),STATUS='OLD',               &
     &      FORM='UNFORMATTED',ACCESS='DIRECT',RECL=IRECLN,ERR=140)

!         READ THE BAND MODEL FILE HEADER.  IBNDWD IS THE WIDTH (CM-1)
          NREC=1
          MESSAG=' HEADER'
          READ(IBNARY,REC=NREC,IOSTAT=IOS)NTEMP,(TBAND(IT),IT=1,NTEMP), &
     &      IBNDWD,IF1ST,IFLAST,LSTREC,NDIVID,DEDGE
          IF(DEDGE.EQ.0. .OR. IOS.NE.0)THEN

!             OLD FORMAT
              READ(IBNARY,REC=NREC,ERR=140)NTEMP,(TBAND(IT),IT=1,NTEMP),&
     &          IBNDWD,IF1ST,IFLAST,LSTREC,DEDGE
              NDIVID=1
          ENDIF
          WRITE(IASCII,'(I3,0P11F7.0:,/(3X,0P11F7.0))')                 &
     &      NTEMP,(TBAND(IT),IT=1,NTEMP)
          WRITE(IASCII,'(5I8,F8.3)')                                    &
     &      IBNDWD,IF1ST,IFLAST,LSTREC,NDIVID,DEDGE

!         ECHO HEADER INFO
          WRITE(*,'(/5X,A,/I3,0P11F7.0)')                               &
     &      'NTEMP,(TBAND(IT),IT=1,NTEMP)',NTEMP,(TBAND(IT),IT=1,NTEMP)
          WRITE(*,'(/2(A,I7,5X),A,I7,/2(A,I7,5X),A,F7.3)')              &
     &      'IBNDWD=',IBNDWD,' IF1ST=', IF1ST,'IFLAST=',IFLAST,         &
     &      'LSTREC=',LSTREC,'NDIVID=',NDIVID,' DEDGE=', DEDGE

!         READ DATA
          MESSAG='  DATA '
          NREC=NREC+1
          READ(IBNARY,REC=NREC,ERR=140)                                 &
     &      IBIN,IMOL,(SD(IT),IT=1,NTEMP),IALF,(OD(IT),IT=1,NTEMP)
          WRITE(IASCII,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
          WRITE(IASCII,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)
  120     CONTINUE
          NREC=NREC+1
          READ(IBNARY,REC=NREC,ERR=130)                                 &
     &      IBIN,IMOL,(SD(IT),IT=1,NTEMP),IALF,(OD(IT),IT=1,NTEMP)
          WRITE(IASCII,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
          WRITE(IASCII,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)
          IF(8000*(NREC/8000).EQ.NREC)THEN

!             WRITE EACH 8000 RECORDS TO KEEP USER AWARE OF PROGRESS.
              WRITE(*,'(/A,I7,A)')' BAND MODEL RECORD',NREC,' IS:'
              WRITE(*,'(I6,I5,1P11E11.3)')IBIN,IMOL,(SD(IT),IT=1,NTEMP)
              WRITE(*,'(6X,I5,1P11E11.3)')IALF,(OD(IT),IT=1,NTEMP)
          ENDIF
          GOTO 120
  130     CONTINUE
          NREC=NREC-1
          WRITE(*,'(/3(A,I7))')                                         &
     &      ' BAND MODEL PARAMETER FILE CONTAINS',NREC,                 &
     &      ' RECORDS (LAST FREQUENCY IS',IFLAST,' CM-1)'
          CLOSE(IASCII,STATUS='KEEP')
          CLOSE(IBNARY,STATUS='KEEP')
          WRITE(*,'(/2A,/5X,A)')' SUCCESSFULLY CREATED THE ASCII',      &
     &      ' (FORMATTED) BAND MODEL FILE:',ASCNAM(1:LENASC)
          STOP

!         UNABLE TO READ BINARY FILE
  140     CONTINUE
          CLOSE(IASCII,STATUS='DELETE')
          CLOSE(IBNARY,STATUS='KEEP')
          IF(IRECLN.LT.MXRCLN)THEN
              WRITE(*,FMT='(/(2A,I8,A))')' AN ERROR OCCURRED',          &
     &          ' WHEN A RECORD LENGTH OF',IRECLN,' WAS USED.'
              IF(IRECLN.EQ.MXRCLN-4)THEN
                  IRECLN=MXRCLN
              ELSE
                  IRECLN=2*IRECLN
              ENDIF
              WRITE(*,FMT='((A,I8,A))')                                 &
     &          ' A RECORD LENGTH OF',IRECLN,' WILL NOW BE TRIED.'
              GOTO 110
          ENDIF
  150     CONTINUE
          IF(LENBIN.GT.0)WRITE(*,'(/(5A))')' ERROR:  UNABLE',           &
     &      ' TO READ',MESSAG,' FROM BINARY FILE:  ',BINNAM(1:LENBIN),  &
     &      '         NO ASCII FILE WAS CREATED.'
          WRITE(*,'(/A,I8)')                                            &
     &      ' LAST (AND LARGEST) RECORD LENGTH TRIED WAS',IRECLN
          STOP
      ELSE
          GOTO 10
      ENDIF
      END
      INTEGER FUNCTION MINLEN(STRING)

!     THIS ROUTINE ELIMINATES LEADING BLANKS FROM STRING, AND
!     DETERMINES LENGTH OF FIRST CHARACTER STRING.

!     DECLARE VARIABLES
      CHARACTER*(*) STRING
      INTEGER LENGTH,ISTART,I

!     POSITION OF FIRST NON-BLANK CHARACTER
      LENGTH=LEN(STRING)
      DO ISTART=1,LENGTH
          IF(STRING(ISTART:ISTART).NE.' ')GOTO 10
      ENDDO

!     BLANK STRING
      MINLEN=0
      RETURN

!     ELIMINATE LEADING BLANKS
   10 CONTINUE
      STRING(1:LENGTH-ISTART+1)=STRING(ISTART:LENGTH)

!     ADD TRAILING BLANKS
      DO I=LENGTH-ISTART+2,LENGTH
          STRING(I:I)=' '
      ENDDO

!     DETERMINE LENGTH OF FIRST CHARACTER STRING BY FINDING FIRST BLANK
      MINLEN=INDEX(STRING,' ')-1
      IF(MINLEN.LT.0)MINLEN=LENGTH
      RETURN
      END
