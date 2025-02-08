      PROGRAM CKBIN

!     ROUTINE TO CREATE CORRELATED-K DISTRIBUTION DATA BINARY FILE.

!     PARAMETERS:
!       MXKSUB   DIMENSION OF K-DISTRIBUTION SUB-INTERVAL ARRAY.
!       MXGAML   DIMENSION OF LORENTZ HALF-WIDTH ARRAY.
!       MXGAMD   DIMENSION OF DOPPLER HALF-WIDTH ARRAY.
!       MXNUML   DIMENSION OF EFFECTIVE NUMBER OF LINES ARRAY.
      INCLUDE 'PARAMS.h'

!     COMMONS:

!     COMMON /CORKDT/
!       WTKSUB   SPECTRAL BIN SUB-INTERVAL FRACTIONAL WIDTHS.
!       DEPLAY   INCREMENTAL OPTICAL DEPTHS
!       TRNLAY   INCREMENTAL TRANSMITTANCES
!       TRNCUM   CUMULATIVE TRANSMITTANCES
      REAL WTKSUB,DEPLAY,TRNLAY,TRNCUM
      COMMON/CORKDT/WTKSUB(MXKSUB),DEPLAY(MXKSUB),                      &
     &  TRNLAY(MXKSUB),TRNCUM(MXKSUB)
      SAVE /CORKDT/

!     COMMON /CORKTB/
!       GAMLIN   LORENTZ HALF-WIDTH BOUNDARY VALUES [CM-1].
!       GAMDIN   DOPPLER HALF-WIDTH BOUNDARY VALUES [CM-1].
!       RLININ   EFFECTIVE NUMBER OF LINES BOUNDARY VALUES.
!       VAL      ABSORPTION COEFFICIENT TABLE [ATM-1 CM-1].
      INTEGER NGAML,NGAMD,NNUML
      REAL GAMLIN,GAMDIN,RLININ,VAL
      COMMON/CORKTB/NGAML,NGAMD,NNUML,GAMLIN(MXGAML),GAMDIN(MXGAMD),    &
     &  RLININ(MXNUML),VAL(1:MXGAML,1:MXGAMD,1:MXNUML,0:MXKSUB)
      SAVE /CORKTB/

!     DECLARE LOCAL VARIABLES
      CHARACTER FILNAM*130,YESNO*1
      INTEGER IKSUB,IFILE,ITEST,IKSBM1,IGAML,IGAMD,INUML,I
      LOGICAL LTEST
      REAL WTKSB0,GAML,GAMD,RLIN,VALOLD,VALNEW

!     LIST DATA
      DATA IFILE/9/

!     READ ASCII FILE NAME
   10 WRITE(*,'(/A)')' Enter name of Correlated-K ASCII data file'
      READ(*,'(A)')FILNAM

!     TEST FOR EXISTENCE OF FILE
      INQUIRE(FILE=FILNAM,EXIST=LTEST)
      IF(.NOT.LTEST)THEN
          WRITE(*,'(/(A))')                                             &
     &      'No file named',FILNAM,'was found.','Please try again.'
          GOTO 10
      ENDIF

!     OPEN CORRELATED-K DATA FILE
      OPEN(IFILE,FILE=FILNAM,STATUS='OLD')
      WRITE(*,'(/(A))')' Reading file',FILNAM

!     READ IN K-DISTRIBUTION WEIGHTS
      READ(IFILE,'(//I10,7F10.7:,/(10X,7F10.7:))')                      &
     &  NKSUB,WTKSB0,(WTKSUB(IKSUB),IKSUB=1,NKSUB-1)
      NKSUB=NKSUB-1
      IF(NKSUB.GT.MXKSUB)THEN
          WRITE(*,'(/2A,I3,A,/A)')                                      &
     &      ' ERROR:  Parameter MXKSUB (in PARAM.LST) must',            &
     &      ' equal or exceed',NKSUB,' to use file',FILNAM
          STOP
      ELSEIF(WTKSB0.NE.0. .AND. WTKSUB(NKSUB).NE.1.)THEN
         STOP ' ERROR:  Incorrect cumulative distribution values'
      ENDIF
      IKSUB=NKSUB
      DO IKSBM1=NKSUB-1,1,-1
          WTKSUB(IKSUB)=WTKSUB(IKSUB)-WTKSUB(IKSBM1)
          IF(WTKSUB(IKSUB).LE.0.)STOP                                   &
     &      ' ERROR:  Incorrect cumulative distribution values'
          IKSUB=IKSBM1
      ENDDO

!     READ IN LORENTZ HALF-WIDTHS [CM-1]
      READ(IFILE,'(/I5,5X,6E12.6:,/(10X,6E12.6:))')                     &
     &  NGAML,(GAMLIN(IGAML),IGAML=1,NGAML)
      IF(NGAML.GT.MXGAML)THEN
          WRITE(*,'(/2A,I3,A,/A)')                                      &
     &      ' ERROR:  Parameter MXGAML (in PARAM.LST) must',            &
     &      ' equal or exceed',NGAML,' to use file',FILNAM
          STOP
      ENDIF
      I=1
      DO IGAML=2,NGAML
          IF(GAMLIN(IGAML).GE.GAMLIN(I))STOP                            &
     &      ' ERROR:  LORENTZ HALF-WIDTHS NOT IN DECREASING ORDER'
          I=IGAML
      ENDDO

!     READ IN DOPPLER HALF-WIDTHS [CM-1]
      READ(IFILE,'(/I5,5X,6E12.6:,/(10X,6E12.6:))')                     &
     &  NGAMD,(GAMDIN(IGAMD),IGAMD=1,NGAMD)
      IF(NGAMD.GT.MXGAMD)THEN
          WRITE(*,'(/2A,I3,A,/A)')                                      &
     &      ' ERROR:  Parameter MXGAMD (in PARAM.LST) must',            &
     &      ' equal or exceed',NGAMD,' to use file',FILNAM
          STOP
      ENDIF
      I=1
      DO IGAMD=2,NGAMD
          IF(GAMDIN(IGAMD).GE.GAMDIN(I))STOP                            &
     &      ' ERROR:  DOPPLER HALF-WIDTHS NOT IN DECREASING ORDER'
          I=IGAMD
      ENDDO

!     READ IN EFFECTIVE NUMBER OF LINES.
      READ(IFILE,'(/I10,7F10.2:,/(10X,7F10.2:))')                       &
     &  NNUML,(RLININ(INUML),INUML=1,NNUML)
      IF(NNUML.GT.MXNUML)THEN
          WRITE(*,'(/2A,I3,A,/A)')                                      &
     &      ' ERROR:  Parameter MXNUML (in PARAM.LST) must',            &
     &      ' equal or exceed',NNUML,' to use file',FILNAM
          STOP
      ENDIF
      I=1
      DO INUML=2,NNUML
          IF(RLININ(INUML).LE.RLININ(I))STOP 'ERROR:                    &
     &      EFFECTIVE NUMBER OF LINES NOT IN INCREASING ORDER'
          I=INUML
      ENDDO

!     SKIP TWO LINES
      READ(IFILE,'(/20X,I10)')ITEST

!     LOOP OVER LORENTZ HALF-WIDTHS
      DO IGAML=1,NGAML

!         LOOP OVER DOPPLER HALF-WIDTHS
          DO IGAMD=1,NGAMD
              READ(IFILE,'(2E12.6)')GAML,GAMD
              IF(GAML.NE.GAMLIN(IGAML) .OR. GAMD.NE.GAMDIN(IGAMD))THEN
                  WRITE(*,'(/A,/(8X,A,I2,A,2(E12.6,A)))')               &
     &              ' ERROR:  HALF-WIDTH MISMATCH.',                    &
     &              ' GAMLIN(',IGAML,') = ',GAMLIN(IGAML),              &
     &              ' CM-1     GAML = ',GAML,' CM-1',                   &
     &              ' GAMDIN(',IGAMD,') = ',GAMDIN(IGAMD),              &
     &              ' CM-1     GAMD = ',GAMD,' CM-1'
                  STOP
              ENDIF

!             LOOP OVER EFFECTIVE NUMBER OF LINES
              DO INUML=1,NNUML

!                 READ IN NORMALIZED ABSORPTION COEFFIECIENTS
                  READ(IFILE,'(F10.2,7E10.4:,/(10X,7E10.4))')           &
     &              RLIN,(VAL(IGAML,IGAMD,INUML,IKSUB),IKSUB=0,NKSUB)
                  IF(RLIN.NE.RLININ(INUML))THEN
                      WRITE(*,'(/A,/8X,A,I2,2(A,F8.2))')                &
     &                  ' ERROR:  EFFECTIVE NUMBER OF LINES MISMATCH.', &
     &                  ' RLININ(',INUML,') = ',RLININ(INUML),          &
     &                  '      RLIN = ',RLIN
                      STOP
                  ENDIF

!                 CHECK MONOTONICITY OF ABSORPTION COEFFICIENTS
                  VALOLD=VAL(IGAML,IGAMD,INUML,0)
                  DO IKSUB=1,NKSUB
                      VALNEW=VAL(IGAML,IGAMD,INUML,IKSUB)
                      IF(VALNEW.LT.VALOLD)THEN
                          WRITE(*,'(/2A,2(/8X,A,E10.4),                 &
     &                      /8X,A,F10.4,//8X,A,/(14X,6(1X,E9.4)))')     &
     &                      ' ERROR:  DECREASING',                      &
     &                      ' ABSORPTION COEFFICIENTS AT',              &
     &                      ' LORENTZ HALF-WIDTH [CM-1] =',GAML,        &
     &                      ' DOPPLER HALF-WIDTH [CM-1] =',GAMD,        &
     &                      ' EFFECTIVE NUMBER OF LINES =',RLIN,        &
     &                      ' NORMALIZED ABSORPTION COEFFICIENTS:',     &
     &                      (VAL(IGAML,IGAMD,INUML,I),I=0,NKSUB)
                          STOP
                      ENDIF
                      VALOLD=VALNEW
                  ENDDO
              ENDDO
          ENDDO
      ENDDO

!     CLOSE CORRELATED-K DATA FILE
      CLOSE(IFILE)
      WRITE(*  ,'(/(A))')'Successfully read file',FILNAM

!     READ BINARY FILE NAME
   20 WRITE(*,'(/A)')' Enter name of Correlated-K BINARY data file'
      READ(*,'(A)')FILNAM

!     TEST FOR EXISTENCE OF FILE
      INQUIRE(FILE=FILNAM,EXIST=LTEST)
      IF(LTEST)THEN
          WRITE(*,'(/(A))')'A file named',FILNAM,'already exists.',     &
     &      'Do you wish to overwrite it (Y/N).'
          READ(*,'(A)')YESNO
          IF(YESNO.NE.'Y' .AND. YESNO.NE.'y')GOTO 20
          OPEN(IFILE,FILE=FILNAM,STATUS='OLD')
          CLOSE(IFILE,STATUS='DELETE')
      ENDIF

!     OPEN BINARY FILE
      OPEN(IFILE,FILE=FILNAM,STATUS='NEW',FORM='UNFORMATTED')

!     WRITE DATA TO BINARY FILE
      WRITE(IFILE)NKSUB,NGAML,NGAMD,NNUML
      WRITE(IFILE)                                                      &
     &  (WTKSUB(IKSUB),IKSUB=1,NKSUB),(GAMLIN(IGAML),IGAML=1,NGAML),    &
     &  (GAMDIN(IGAMD),IGAMD=1,NGAMD),(RLININ(INUML),INUML=1,NNUML)
      DO IKSUB=0,NKSUB
          WRITE(IFILE)(((VAL(IGAML,IGAMD,INUML,IKSUB),                  &
     &      IGAML=1,NGAML),IGAMD=1,NGAMD),INUML=1,NNUML)
      ENDDO

!     STOP
      STOP 'SUCCESSFUL BINARY WRITE'
      END
