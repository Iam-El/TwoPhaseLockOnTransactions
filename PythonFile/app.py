# Group 1
# Elsy Fernandes 1001602253
# Maria Lancy 1001639262
import os
import re
from prettytable import PrettyTable

# declaring variables needed
fileLine = []
counter = []
transactionObjects = []
lockObjects = []
executinop = []

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'templates')
print(templates_dir)

transactionsWaiting = []
waitingop = []
abortingTransaction = []
restart = []

# declaring and defining Transaction Table which contains TransactionId,Transaction state,Timestamp
class transactionTable():
    def __init__(self, tranID, Timestamp, State, lockBy, lockedOp):
        self.tranID = tranID
        self.Timestamp = Timestamp
        self.State = State
        if lockedOp == None:
            self.lockedOp = []
        else:
            self.lockedOp = [lockedOp]
        self.itemsLockedByTransaction = []
        self.waitingop = []
        self.lockBy = lockBy
        self.waitingop.append(tranID)

    # This function adds list of items locked by the transaction to the transaction
    def itemLockedByTransaction(self, dataitem):
        self.itemsLockedByTransaction.append(dataitem)

    # This function is used to change the transaction state
    def changeState(self, newstate):
        self.State = newstate

    # This function is used to denote which data items are locked by which transaction
    def newlockedby(self, newlockedby):
        self.lockBy = newlockedby

    # This operation is used to tell which operation is in waiting state for a transaction
    def lockop(self, newlockop):
        if not (newlockop in self.lockedOp):
            self.lockedOp.append(newlockop)

    def toString(self):
        op = ''
        op = op.join(self.tranID)
        op = op + '-'
        op = op.join(self.State)
        op = op + '-'
        op = op.join(self.lockBy)
        op = op + '-'
        print(op.join(self.lockedOp))

# This class is used to define lock table which contains information about data item locked like data item name,
# Type of lock ,Locked by which transaction
class lockedTable():
    def __init__(self, dataitem, lock, tranID):
        self.dataitem = dataitem
        self.lock = lock
        self.tranID = tranID
        self.transactionIDHoldingWriteLock = []
        self.transactionIDHoldingReadLock = []

        self.transactionWaiting = []
        self.transactionWaiting.append(tranID)

        self.abortingTransaction = []
        self.abortingTransaction.append(tranID)

        self.transactionIDHoldingReadLock = []
        self.transactionIDHoldingReadLock.append(tranID)

    # This functions add transaction which have read lock on items
    def transactionIDHoldingReadLockFun(self, tranID):
        self.transactionIDHoldingReadLock.append(tranID)

    # This function is used to change lock state of a data item in lock table
    def changeLockState(self, lock):
        self.lock = lock

# This function is called when a transaction begins for the first time
# We add the Transaction to the transaction table with its Id,timestamp,Active state
def beginDatabaseTransaction(j, writefile):
    for k in j:
        if k.isdigit():
            digit = k.split()
    print(
        "************************************************************************************************************")
    writeToFile(writefile,
                "*********************************************************************************************")

    print('Begin Transaction for Transaction num: ' + str(digit))
    writeToFile(writefile, 'Begin Transaction for Transaction num: ' + str(digit))

    timestamp = len(counter) + 1
    transactionObjects.append(transactionTable(digit, timestamp, 'Active', None, None))
    counter.append(1)
    printTable(transactionObjects)

# This function is called when a read lock on data item is requested
# It checks if lock table is empty,it grants read lock to transaction and updates the lock and transaction table
# If lock table is not empty,it checks if requested data item is already on lock table
# if present it checks whether it is read locked or write locked.
# If read locked ,it grants read lock to transaction and updates the lock and transaction table
# If write locked, it calls wound wait function and passes lock holding Tid and lock requesting Tid as inputs
# If lock table is not empty,it checks if requested data item is already on lock table
# If not present it grants read lock to transaction and updates the lock and transaction table
def read(j, writefile):
    readflag = 0
    if j == 'Ignore':
        print('Ignore the operation')
    else:

        for k in j:
            if k.isdigit():
                digit = k.split()

        dataitem = re.search(r"\(([A-Za-z0-9_]+)\)", j).group(1)
        print('Data Item is :' + dataitem)
        writeToFile(writefile, 'Data Item is :' + dataitem)

        if len(lockObjects) == 0:
            lockObjects.append(lockedTable(dataitem, 'ReadLock', digit))
            for t in transactionObjects:
                if t.tranID == digit:
                    t.itemLockedByTransaction(dataitem)
                    print(
                        "Transaction for Data Item "'\t' + dataitem + '\t'"is Read locked by the transaction"'\t' + str(
                            digit))
                    writeToFile(writefile,
                                "Transaction for Data Item "'\t' + dataitem + '\t'"is Read locked by the transaction"'\t' + str(
                                    digit))
                    writeToFile(writefile, "\n")
        elif len(lockObjects) != 0:
            length = len(lockObjects)
            for i in range(0, length):
                if lockObjects[i].dataitem == dataitem:
                    readflag = 1
                    if lockObjects[i].lock == 'ReadLock':
                        lockObjects.append(lockedTable(dataitem, 'ReadLock', digit))
                        lockObjects[i].transactionIDHoldingReadLockFun(digit)
                        for t in transactionObjects:
                            if t.tranID == digit:
                                t.itemLockedByTransaction(dataitem)
                        print(
                            "Transaction for Data Item "'\t' + dataitem + '\t' " Read locked by the transaction" '\t' + str(
                                digit))
                        writeToFile(writefile,
                                    "Transaction for Data Item "'\t' + dataitem + '\t'"is Read locked by the transaction"'\t' + str(
                                        digit))
                        writeToFile(writefile, "\n")
                        break
                    else:
                        tran = str(lockObjects[i].transactionIDHoldingReadLock[0])
                        holdingTran = lockObjects[i].transactionIDHoldingReadLock[0]
                        print(
                            "Conflicting : Transaction for Data Item is"'\t' + dataitem + '\t' "is already Write Lock by Transaction" '\t'
                            + tran)
                        writeToFile(writefile,
                                    "Conflicting : Transaction for Data Item is"'\t' + dataitem + '\t' "is already Write Lock by Transaction" '\t'
                                    + tran)
                        writeToFile(writefile, "\n")

                        woundWait(digit, holdingTran, j)

            if readflag == 0:
                lockObjects.append(lockedTable(dataitem, 'ReadLock', digit))
                for t in transactionObjects:
                    if t.tranID == digit:
                        t.itemLockedByTransaction(dataitem)
                print("Transaction for Data Item "'\t' + dataitem + '\t' " Read locked by the transaction", str(digit))
                writeToFile(writefile,
                            "Transaction for Data Item "'\t' + dataitem + '\t'"is Read locked by the transaction"'\t' + str(
                                digit))
                writeToFile(writefile, "\n")

        locktable = PrettyTable(['dataitem', 'lock', 'tranID'])
        for lockvalues in lockObjects:
            locktable.add_row([lockvalues.dataitem, lockvalues.lock, lockvalues.tranID])
        print('Lock Table :-')
        writeToFile(writefile, 'Lock Table :-')

        print(locktable)
        writeToFile(writefile, str(locktable))

# This function is called when a write lock on data item is requested
# It checks if lock table is empty then it grants write lock to transaction and updates the lock and transaction table
# If lock table is not empty,it checks if requested data item is already on lock table
# if present it checks whether it is read locked or write locked.
# If read locked ,it checks whether Tid which holds read lock is same as one requesting write lock
# If so it grants write lock to transaction and updates the lock and transaction table
# If they are many Tid holding read lock for data Item it calls wound wait
# If not same Tid as requesting,it calls wound wait function and passes lock holding Tid and lock requesting Tid
# If item is already write locked it calls wound wait function and passes lock holding Tid and lock requesting Tid
# If lock table is not empty,it checks if requested data item is already on lock table
# If not present it grants write lock to transaction and updates the lock and transaction table
def write(j, writefile):
    if j == 'Ignore':
        print('Ignore the operation')
    else:
        writeflag = 0
        for k in j:
            if k.isdigit():
                digit = k.split()

        dataitem = re.search(r"\(([A-Za-z0-9_]+)\)", j).group(1)
        print('Data Item is :' + dataitem)
        writeToFile(writefile, 'Data Item is :' + dataitem)

        if len(lockObjects) == 0:
            lockObjects.append(lockedTable(dataitem, 'WriteLock', digit))
            for t in transactionObjects:
                if t.tranID == digit:
                    t.itemLockedByTransaction(dataitem)
                    print(
                        "Transaction for Data Item "'\t' + dataitem + '\t'"is Write locked by the transaction"'\t' + str(
                            digit))
                    writeToFile(writefile,
                                "Transaction for Data Item "'\t' + dataitem + '\t'"is Write locked by the transaction"'\t' + str(
                                    digit))
                    writeToFile(writefile, "\n")

            locktable = PrettyTable(['dataitem', 'lock', 'tranID'])
            for lockvalues in lockObjects:
                locktable.add_row([lockvalues.dataitem, lockvalues.lock, lockvalues.tranID])
            print(locktable)
            writeToFile(writefile, str(locktable))

        elif len(lockObjects) != 0:
            length = len(lockObjects)
            count = 0
            for i in range(0, length):
                if lockObjects[i].dataitem == dataitem:
                    count += 1
            for i in range(0, length):
                if lockObjects[i].dataitem == dataitem:
                    writeflag = 1
                    if lockObjects[i].lock == 'ReadLock':
                        if len(lockObjects[i].transactionIDHoldingReadLock) == 1:
                            if lockObjects[i].transactionIDHoldingReadLock[0] == digit and count <= 1:
                                lockObjects[i].lock = 'WriteLock'
                                print(
                                    "Upgrading the Read Lock to Write Lock on Data Item" '\t' + dataitem + '\t' "by the Transaction" '\t' + str(
                                        digit))
                                writeToFile(writefile,
                                            "Upgrading the Read Lock to Write Lock on Data Item" '\t' + dataitem + '\t' "by the Transaction" '\t' + str(
                                                digit))
                                writeToFile(writefile, "\n")


                            elif lockObjects[i].transactionIDHoldingReadLock[0] != digit:
                                holdingTran = lockObjects[i].transactionIDHoldingReadLock[0]
                                holdingTranstr = str(lockObjects[i].transactionIDHoldingReadLock[0])
                                print(
                                    "Transaction for the the Data Item" '\t' + dataitem + '\t'" is Read Locked by the Transaction"'\t' + holdingTranstr + '\t' ".Hence , Cannot perform Write operation on it!!")
                                writeToFile(writefile,
                                            "Transaction for the the Data Item" '\t' + dataitem + '\t'" is Read Locked by the Transaction"'\t' + holdingTranstr + '\t' ".Hence , Cannot perform Write operation on it!!")
                                writeToFile(writefile, "\n")
                                woundWait(digit, holdingTran, j)
                                break

                        elif (digit != lockObjects[i].transactionIDHoldingReadLock[0]):
                            holdingTran = lockObjects[i].transactionIDHoldingReadLock[0]
                            holdingTranstr = str(lockObjects[i].transactionIDHoldingReadLock[0])
                            print(
                                "Transaction for the Data Item" '\t' + dataitem + '\t'" is Read Locked by the Transaction"'\t' + holdingTranstr + '\t' ".Hence , Cannot perform Write operation on it!!")
                            writeToFile(writefile,
                                        "Transaction for the Data Item" '\t' + dataitem + '\t'" is Read Locked by the Transaction"'\t' + holdingTranstr + '\t' ".Hence , Cannot perform Write operation on it!!")
                            writeToFile(writefile, "\n")
                            woundWait(digit, holdingTran, j)
                            break
                    else:
                        c = 0
                        for lockedresource in lockObjects:
                            if lockedresource.dataitem == dataitem:
                                for temp in lockedresource.transactionIDHoldingReadLock:
                                    if temp == digit:
                                        c += 1
                        holdingTran = lockObjects[i].transactionIDHoldingReadLock[0]
                        print(
                            "Conflicting:Transaction for the Data Item "'\t' + dataitem + '\t' "is already write Locked by the Transaction"'\t' + str(
                                holdingTran) + '\t')
                        writeToFile(writefile,
                                    "Conflicting:Transaction for the Data Item "'\t' + dataitem + '\t' "is already write Locked by the Transaction"'\t' + str(
                                        holdingTran) + '\t')
                        writeToFile(writefile, "\n")
                        woundWait(digit, holdingTran, j)

            if writeflag == 0:
                lockObjects.append(lockedTable(dataitem, 'WriteLock', digit))
                for t in transactionObjects:
                    if t.tranID == digit:
                        t.itemLockedByTransaction(dataitem)
                print("Transaction for Data Item "'\t' + dataitem + '\t' " Write locked by the transaction", str(digit))
                writeToFile(writefile,
                            "Transaction for Data Item "'\t' + dataitem + '\t'"is Write locked by the transaction"'\t' + str(
                                digit))
                writeToFile(writefile, "\n")
        locktable = PrettyTable(['dataitem', 'lock', 'tranID'])
        for lockvalues in lockObjects:
            locktable.add_row([lockvalues.dataitem, lockvalues.lock, lockvalues.tranID])
        print('Lock Table :-')
        writeToFile(writefile, 'Lock Table :-')

        print(locktable)
        writeToFile(writefile, str(locktable))

# This function is called before write lock is obtained by Transaction
# If transaction state is Abort it ignores the operation
def checkwriteState(i, writefile):
    for k in i:
        if k.isdigit():
            digit = k.split()
    for t in transactionObjects:
        if t.tranID == digit:
            if t.State == 'Abort':
                print("Transaction" '\t' + str(digit) + '\t'"is Already Aborted ! Ignore its  operation " + str(i))
                writeToFile(writefile,
                            "Transaction" '\t' + str(digit) + '\t'"is Already Aborted ! Ignore its  operation " + str(
                                i))

                i = 'Ignore'
                write(i, writefile)
            elif t.State == 'Waiting':
                t.lockop(i)
                print("Transaction"'\t' + str(
                    digit) + '\t' "is already in Waiting State. Add the operation to waiting Queue"'\t' + str(i) + '\t')

                writeToFile(writefile,
                            "Transaction"'\t' + str(digit) + '\t' "is already in Waiting State"'\t' + str(i) + '\t')
            elif t.State == 'Active':
                write(i, writefile)

# This function is called before read lock is obtained by Transaction
# If transaction state is Abort it ignores the operation
def checkreadState(i, writefile):
    for k in i:
        if k.isdigit():
            digit = k.split()
    for t in transactionObjects:
        if t.tranID == digit:
            if t.State == 'Abort':
                print("Transaction" '\t' + str(digit) + '\t'"is Already Aborted ! Ignore its  operation " + str(i))
                writeToFile(writefile,
                            "Transaction" '\t' + str(digit) + '\t'"is Already Aborted ! Ignore its  operation " + str(
                                i))
                i = 'Ignore'
                read(i, writefile)
            elif t.State == 'Waiting':
                t.lockop(i)
                print("Transaction"'\t' + str(
                    digit) + '\t' "is already in Waiting State. Add the operation to waiting Queue"'\t' + str(i) + '\t')
                writeToFile(writefile,
                            "Transaction"'\t' + str(digit) + '\t' "is already in Waiting State"'\t' + str(i) + '\t')
            elif t.State == 'Active':
                read(i, writefile)
    printTable(transactionObjects)

# This function performs the wound wait protocol
# If lock requesting Tid < lock holding Tid, then lock Holding Tid is aborted and requesting Tid is given access
# If lock requesting Tid > lock holding Tid, then requesting Tid is changed to waiting state
# and operation is added to its list of waiting operation, which resumes once requesting Tid changes to Active state
def woundWait(requestingT, holdingT, j):
    print('Calling Wound - Wait............')
    writeToFile(writefile, 'Calling Wound - Wait............')
    holdingTstr = str(holdingT)
    for requestingTimestamp in transactionObjects:
        if requestingTimestamp.tranID == requestingT:
            requestTimestamp = requestingTimestamp.Timestamp
            request = requestingTimestamp
    for holdingTimestamp in transactionObjects:
        if holdingTimestamp.tranID == holdingT:
            holdTimestamp = holdingTimestamp.Timestamp
            hold = holdingTimestamp
    if requestTimestamp < holdTimestamp:
        hold.changeState('Abort')
        hold.newlockedby('None')
        hold.lockedOp = []
        print("Aborting the Transaction "'\t' + holdingTstr + '\t')
        writeToFile(writefile, "Aborting the Transaction "'\t' + holdingTstr + '\t')
        abortingTransaction.append(holdingT)
        abort(holdingT)
        print("Performing the Operation:---------")
        if j.find('r') != -1:
            read(j, writefile)
        if j.find('w') != -1:
            write(j, writefile)
    else:
        print("Transaction Waiting"'\t' + str(requestingT) + '\t')
        writeToFile(writefile, "Transaction Waiting"'\t' + str(requestingT) + '\t')
        request.changeState('Waiting')
        request.newlockedby(holdingT)
        if checkDuplicateTransaction(request):
            transactionsWaiting.append(request)
        waitingop.append(j)

        request.lockop(j)

    printTable(transactionObjects)

# This function is used to block same transaction to change to wait state more than once
def checkDuplicateTransaction(transaction):
    print(transaction.tranID)
    for t in transactionsWaiting:
        if t.tranID == transaction.tranID:
            return 0
    return 1

# This Function is called when Transaction is aborted
# It changes the transaction state to Abort and unlocks all locks held by the transaction
# It updates lock and transaction table
def abort(holdingT):
    holdingTstr = str(holdingT)
    print("Unlocking all the dataitems held by"'\t' + holdingTstr + '\t')
    writeToFile(writefile, "Unlocking all the data items held by"'\t' + holdingTstr + '\t')
    for t in transactionObjects:
        if t.tranID == holdingT:
            for lock in t.itemsLockedByTransaction:
                for dataitem in lockObjects:
                    if dataitem.dataitem == lock:
                        if len(dataitem.transactionIDHoldingReadLock) == 1 and dataitem.tranID == holdingT:
                            lockObjects.remove(dataitem)

                        elif dataitem.tranID == holdingT:
                            lockObjects.remove(dataitem)
                            break
    startblockTrans(holdingT)

# This Function is called to execute waiting operations when transaction is committed and released all locks
# so that any waiting transaction can execute its waiting operation, acquire lock and go to active state
# Updates Transaction and lock table
def startblockTrans(holdingT):
    for t in transactionsWaiting:
        if t.State == 'Abort':
            transactionsWaiting.remove(t)

        else:
            for i in transactionObjects:
                if i.lockBy == holdingT and i.State == 'Waiting':

                    s = 0
                    while s < len(i.lockedOp) and i.lockBy == holdingT:
                        print('Attempting to perform the operation' '\t' + i.lockedOp[s])
                        writeToFile(writefile, 'Attempting to perform the operation' '\t' + i.lockedOp[s])
                        transaction = i.lockedOp.pop(0)
                        if transaction.find('r') != -1:
                            read(transaction, writefile)
                        if transaction.find('w') != -1:
                            write(transaction, writefile)
                    if i.lockBy == holdingT:
                        i.State = 'Active'
                        i.lockBy = None

# Function to print the contents of the Transaction table
def printTable(transactionobjects):
    transactiontable = PrettyTable(['tranID', 'Timestamp', 'State', 'Lockedby', 'Locked Operation'])
    for i in transactionobjects:
        transactiontable.add_row([i.tranID, i.Timestamp, i.State, i.lockBy, i.lockedOp])
    print('Transaction Table :-')
    print(transactiontable)
    writeToFile(writefile, 'Transaction Table :-')
    writeToFile(writefile, str(transactiontable))

# Function to write the output in a output text file
def writeToFile(file, message):
    file.writelines(message)
    file.writelines('\n')

# This function is called when commit operation is requested
# Commits the transaction and unlocks all data items held by transaction
# Changes transaction state to Commit
# Updates lock and transaction table

def end(i, writefile):
    for k in i:
        if k.isdigit():
            digit = k.split()
    for t in transactionObjects:

        if t.tranID == digit and t.State != 'Abort' and t.State != 'Waiting':
            print("Committing transaction"'\t' + str(digit))
            writeToFile(writefile, "Committing transaction"'\t' + str(digit))

            t.State = 'Commit'
            t.lockedOp = []
            abort(digit)
        elif t.tranID == digit and t.State == 'Abort':
            print('Transaction''\t' + str(digit) + '\t'' is Already Aborted!!')
            writeToFile(writefile, 'Transaction''\t' + str(digit) + '\t'' is Already Aborted!!')

            abort(digit)
        elif t.tranID == digit and t.State == 'Waiting':
            print('Since state is in waiting, cannot commit transaction''\t' + str(digit))
            writeToFile(writefile, 'Since state is in waiting, cannot commit transaction''\t' + str(digit))
    printTable(transactionObjects)

# Reads input file and perform operation requested
val = input("Enter File Name: ")
filename = val
if filename == 'file1.txt':
    writefile = open("output1.txt", "a")
if filename == 'file2.txt':
    writefile = open("output2.txt", "a")
if filename == 'file3.txt':
    writefile = open("output3.txt", "a")
if filename == 'file4.txt':
    writefile = open("output4.txt", "a")
if filename == 'file5.txt':
    writefile = open("output5.txt", "a")
if filename == 'file6.txt':
    writefile = open("output6.txt", "a")
if filename == 'file7.txt':
    writefile = open("output7.txt", "a")
lines = [line.rstrip('\n') for line in open(filename)]
for line in lines:
    fileLine.append(line)
for i in fileLine:
    print("Looking into operation\n" + i)
    writeToFile(writefile, "Looking into operation\n" + i)
    if i.find('b') != -1:
        beginDatabaseTransaction(i, writefile)
    if i.find('r') != -1:
        print('Beginning of Read Operation :-')
        writeToFile(writefile, 'Beginning of Read Operation :-\n')
        checkreadState(i, writefile)
    if i.find('w') != -1:
        print('Beginning of Write Operation :-')
        writeToFile(writefile, 'Beginning of Write Operation :-\n')
        checkwriteState(i, writefile)
    if i.find('e') != -1:
        print('End Database Transaction')
        writeToFile(writefile, 'End Operation :-\n')
        end(i, writefile)
