// for testing: import_test
// for production: journal
const JOURNAL_TABLE = "import_test";
const BIZ_LINE = "Bridal";

const NULL_NUMERIC = 2;
const NULL_INT = 4;
const NULL_DOUBLE = 8;
const NULL_VARCHAR = 12;
const NULL_BOOLEAN = 16;
const NULL_DATE = 91;

// column indices in data tables
const TRANS_BIZ_LOC = 0;
const TRANS_STAFF_ID = 1;
const TRANS_STAFF_ALIAS = 2;
const TRANS_RECEIPT_ID = 4;
const TRANS_COORDINATOR_NAME = 5;
const TRANS_CLIENT_NAMES = 6;
const TRANS_EVENT_DATE = 7;
const TRANS_RECEIPT_AMOUNT = 8;
const TRANS_SALE_AMOUNT = 9;
const TRANS_RENTAL_AMOUNT = 10;
const SUMMARY_BIZ_LOC = 0;
const SUMMARY_TRANS_TYPE = 1;
const SUMMARY_TRANS_SUBTYPE1 = 2;
const SUMMARY_TRANS_SUBTYPE2 = 3;
const SUMMARY_DAY_TOTAL = 4;
const RECEIPT_COORDINATOR_NAME = 1
const RECEIPT_CLIENT_NAMES = 2;
const RECEIPT_EVENT_DATE = 3;
const RECEIPT_PACKAGE_AMOUNT = 4;
const RECEIPT_LAST_AMEND_DATE = 5;
const RECEIPT_UNPAID_BALANCE = 6;

const URL = "jdbc:mysql://s1-db.ddns.net:3306/s1";
var conn;
var batchDate;
var batchRef;

function postDailyRevenue2DB() {
  // set Batch Reference according to the date in the spreadsheet
  var transDate = SpreadsheetApp.getActiveSpreadsheet().getRangeByName("TransDate");
  dateValue = transDate.getValue();
  batchDate = Utilities.formatDate(dateValue, Session.getScriptTimeZone(), "yyyy-MM-dd");
  batchRef = Utilities.formatDate(dateValue, Session.getScriptTimeZone(), "yyyyMMdd") + "-0";

  // remove transactions previously posted from posting log and journal
  conn = Jdbc.getConnection(URL, "horace", "Luv!270211");
  var stmtCleanUp = conn.prepareStatement("delete from import_daily_trans where batch_ref = ?");
  stmtCleanUp.setString(1, batchRef);
  stmtCleanUp.execute();
  stmtCleanUp.close();
  stmtCleanUp = conn.prepareStatement("delete from import_daily_summary where batch_ref = ?");
  stmtCleanUp.setString(1, batchRef);
  stmtCleanUp.execute();
  stmtCleanUp.close();
  stmtCleanUp = conn.prepareStatement("delete from " + JOURNAL_TABLE + " where batch_ref = ?");
  stmtCleanUp.setString(1, batchRef);
  stmtCleanUp.execute();
  stmtCleanUp.close();

  // post transactions
  postTrans();
  postSummary();

  conn.close();
}

function postTrans() {
  var paymentAmount;
  var transBalance;
  var receiptDetails;
  var stmtReadReceipt;
  var stmtInsertReceipt;
  var stmtUpdateReceipt;
  var whereClause;
  var lastReceiptAmount;
  var newPaymentBalance;
  var eventDate;

  // read "Trans" table into array
  var trans = SpreadsheetApp.getActiveSpreadsheet().getRangeByName("Trans");
  values = trans.getValues();

  var rowJournal = 0;
  var rowTrans = 0;
  var is_header = true;

  var stmtJournal = conn.prepareStatement("insert into " + JOURNAL_TABLE
    + " (biz_line, batch_ref, trans_date, trans_type, trans_subtype1, trans_subtype2, "
    + "trans_biz_loc, trans_ref, trans_amount_php) values(?,?,?,?,?,?,?,?,?);");
  var stmtTrans = conn.prepareStatement("insert into import_daily_trans"
    + " (batch_ref, trans_date, biz_loc, staff_id, receipt_number, coordinator_name, "
    + "client_names, event_date, receipt_amount, sale_amount, rental_amount) "
    + "values(?,?,?,?,?,?,?,?,?,?,?);");
  var stmtReadReceipt;

  for (var row in values) {
    if (is_header) {
      is_header = false;
    }
    else {
      paymentAmount = 0;
      if (values[row][TRANS_BIZ_LOC] != "") {
        if (values[row][TRANS_EVENT_DATE] != "") {
          eventDate = Utilities.formatDate(values[row][TRANS_EVENT_DATE], Session.getScriptTimeZone(), "yyyy-MM-dd");
        }
        stmtTrans.setString(1, batchRef);
        stmtTrans.setObject(2, batchDate);
        stmtTrans.setString(3, values[row][TRANS_BIZ_LOC]);
        if (values[row][TRANS_STAFF_ID] == "") { stmtTrans.setNull(4, NULL_INT) }
        else { stmtTrans.setDouble(4, values[row][TRANS_STAFF_ID]) }
        if (values[row][TRANS_RECEIPT_ID] == "") { stmtTrans.setNull(5, NULL_VARCHAR) }
        else { stmtTrans.setString(5, values[row][TRANS_RECEIPT_ID]) }
        if (values[row][TRANS_COORDINATOR_NAME] == "") { stmtTrans.setNull(6, NULL_VARCHAR) }
        else { stmtTrans.setString(6, values[row][TRANS_COORDINATOR_NAME]) }
        if (values[row][TRANS_CLIENT_NAMES] == "") { stmtTrans.setNull(7, NULL_VARCHAR) }
        else { stmtTrans.setString(7, values[row][TRANS_CLIENT_NAMES]) }
        if (values[row][TRANS_EVENT_DATE] == "") { stmtTrans.setNull(8, NULL_DATE) }
        else { stmtTrans.setObject(8, eventDate) }
        if (values[row][TRANS_RECEIPT_AMOUNT] == "") { stmtTrans.setDouble(9, 0) }
        else { stmtTrans.setDouble(9, values[row][TRANS_RECEIPT_AMOUNT]) }
        if (values[row][TRANS_SALE_AMOUNT] == "") { stmtTrans.setDouble(10, 0) }
        else { stmtTrans.setDouble(10, values[row][TRANS_SALE_AMOUNT]) }
        if (values[row][TRANS_RENTAL_AMOUNT] == "") { stmtTrans.setDouble(11, 0) }
        else { stmtTrans.setDouble(11, values[row][TRANS_RENTAL_AMOUNT]) }
        stmtTrans.addBatch();
        rowTrans++;

        if ((values[row][TRANS_RENTAL_AMOUNT] * 1) != 0) {
          paymentAmount = paymentAmount + values[row][TRANS_RENTAL_AMOUNT]
          stmtJournal.setString(1, BIZ_LINE);
          stmtJournal.setString(2, batchRef);
          stmtJournal.setObject(3, batchDate);
          stmtJournal.setString(4, "Income");
          stmtJournal.setString(5, "Rental");
          stmtJournal.setString(6, "Rental");
          stmtJournal.setString(7, values[row][TRANS_BIZ_LOC]);
          if (values[row][TRANS_RECEIPT_ID] == "") { stmtJournal.setNull(8, NULL_VARCHAR) }
          else { stmtJournal.setString(8, values[row][TRANS_RECEIPT_ID]) }
          stmtJournal.setDouble(9, values[row][TRANS_RENTAL_AMOUNT]);
          stmtJournal.addBatch();
          rowJournal++;
        }
        if ((values[row][TRANS_SALE_AMOUNT] * 1) != 0) {
          paymentAmount = paymentAmount + values[row][TRANS_SALE_AMOUNT]
          stmtJournal.setString(1, BIZ_LINE);
          stmtJournal.setString(2, batchRef);
          stmtJournal.setObject(3, batchDate);
          stmtJournal.setString(4, "Income");
          stmtJournal.setString(5, "Retail Sale");
          stmtJournal.setString(6, "Retail Sale");
          stmtJournal.setString(7, values[row][TRANS_BIZ_LOC]);
          if (values[row][TRANS_RECEIPT_ID] == "") { stmtJournal.setNull(8, NULL_VARCHAR) }
          else { stmtJournal.setString(8, values[row][TRANS_RECEIPT_ID]) }
          stmtJournal.setDouble(9, values[row][TRANS_SALE_AMOUNT]);
          stmtJournal.addBatch();
          rowJournal++;
        }

        if (values[row][TRANS_RECEIPT_ID] != "") {
          whereClause = " where receipt_number = '" + values[row][TRANS_RECEIPT_ID] + "'";
          stmtReadReceipt = conn.createStatement();
          receiptDetails = stmtReadReceipt.executeQuery("select coordinator_name, client_names, "
            + "event_date, receipt_amount_php, last_amend_date, unpaid_balance_php "
            + "from client_receipt" + whereClause);
          if (receiptDetails.next()) {
            // Logger.log(receiptDetails.getString(RECEIPT_LAST_AMEND_DATE));
            if (receiptDetails.getString(RECEIPT_LAST_AMEND_DATE) <= batchDate) {
              conn.setAutoCommit(false);
              stmtUpdateReceipt = conn.createStatement();
              if (values[row][TRANS_COORDINATOR_NAME] != "") {
                if (values[row][TRANS_COORDINATOR_NAME] != receiptDetails.getString(RECEIPT_COORDINATOR_NAME)) {
                  stmtUpdateReceipt.executeUpdate("update client_receipt set coordinator_name = '"
                    + values[row][TRANS_COORDINATOR_NAME] + "'" + whereClause);
                }
              }
              if (values[row][TRANS_CLIENT_NAMES] != "") {
                if (values[row][TRANS_CLIENT_NAMES] != receiptDetails.getString(RECEIPT_CLIENT_NAMES)) {
                  stmtUpdateReceipt.executeUpdate("update client_receipt set client_names = '"
                    + values[row][TRANS_CLIENT_NAMES] + "'" + whereClause);
                }
              }
              if (values[row][TRANS_EVENT_DATE] != "") {
                if (values[row][TRANS_EVENT_DATE] != receiptDetails.getString(RECEIPT_EVENT_DATE)) {
                  stmtUpdateReceipt.executeUpdate("update client_receipt set event_date = '"
                    + eventDate + "'" + whereClause);
                }
              }
              lastReceiptAmount = Number(receiptDetails.getString(RECEIPT_PACKAGE_AMOUNT));
              newPaymentBalance = Number(receiptDetails.getString(RECEIPT_UNPAID_BALANCE)) - paymentAmount;
              if (values[row][TRANS_RECEIPT_AMOUNT] == "") {
                // receipt amount blank, no change, just update balance
                stmtUpdateReceipt.executeUpdate("update client_receipt set receipt_amount_php = "
                  + newPaymentBalance.toString() + whereClause);
              }
              else {
                if (values[row][TRANS_RECEIPT_AMOUNT] == lastReceiptAmount) {
                  // receipt amount not blank but no change, just update balance
                  stmtUpdateReceipt.executeUpdate("update client_receipt set receipt_amount_php = "
                    + newPaymentBalance.toString() + whereClause);
                }
                else {
                  // receipt amount not blank and changed, recalc new balance
                  newPaymentBalance = newPaymentBalance + values[row][TRANS_RECEIPT_AMOUNT] - lastReceiptAmount
                  if (newPaymentBalance < 0) { newPaymentBalance = 0 }
                  stmtUpdateReceipt.executeUpdate("update client_receipt set receipt_amount_php = "
                    + values[row][TRANS_RECEIPT_AMOUNT] + ", unpaid_balance_php = "
                    + newPaymentBalance + whereClause);
                }
              }
              stmtUpdateReceipt.executeUpdate("update client_receipt set last_amend_date = '"
                + batchDate + "', updated_on = CURRENT_TIMESTAMP, updated_by = 999" + whereClause);
              conn.commit();
              conn.setAutoCommit(true);
              stmtUpdateReceipt.close();
            }
          }
          else {
            stmtInsertReceipt = conn.prepareStatement("INSERT INTO client_receipt "
              + "(receipt_number, staff_id, trans_biz_loc, coordinator_name, client_names, event_date, "
              + "receipt_amount_php, last_amend_date, unpaid_balance_php, trans_date, created_by) VALUES(?,?,?,?,?,?,?,?,?,?,999)");
            stmtInsertReceipt.setString(1, values[row][TRANS_RECEIPT_ID]);
            stmtInsertReceipt.setString(2, values[row][TRANS_STAFF_ID]);
            stmtInsertReceipt.setString(3, values[row][TRANS_BIZ_LOC]);
            if (values[row][TRANS_COORDINATOR_NAME] == "") { stmtInsertReceipt.setNull(4, NULL_VARCHAR) }
            else { stmtInsertReceipt.setString(4, values[row][TRANS_COORDINATOR_NAME]) }
            if (values[row][TRANS_CLIENT_NAMES] == "") { stmtInsertReceipt.setNull(5, NULL_VARCHAR) }
            else { stmtInsertReceipt.setString(5, values[row][TRANS_CLIENT_NAMES]) }
            if (values[row][TRANS_EVENT_DATE] == "") { stmtInsertReceipt.setNull(6, NULL_DATE) }
            else { stmtInsertReceipt.setObject(6, eventDate) }
            if (values[row][TRANS_RECEIPT_AMOUNT] == "") { stmtInsertReceipt.setDouble(7, 0) }
            else { stmtInsertReceipt.setDouble(7, values[row][TRANS_RECEIPT_AMOUNT]) }
            stmtInsertReceipt.setString(8, batchDate);
            transBalance = values[row][TRANS_RECEIPT_AMOUNT] - paymentAmount;
            if (transBalance < 0) { stmtInsertReceipt.setDouble(9, 0) }
            else { stmtInsertReceipt.setDouble(9, transBalance) }
            stmtInsertReceipt.setString(10, batchDate);
            stmtInsertReceipt.addBatch();
            stmtInsertReceipt.executeBatch();
            stmtInsertReceipt.close();
          }
          stmtReadReceipt.close();
        }
      }
    }
  }

  if (rowTrans > 0) {
    stmtTrans.executeBatch();
  }
  if (rowJournal > 0) {
    stmtJournal.executeBatch();
  }
  stmtTrans.close();
  stmtJournal.close();
}

function postSummary() {
  var transFullType;
  // read "Summary" table into array
  var summary = SpreadsheetApp.getActiveSpreadsheet().getRangeByName("Summary");
  values = summary.getValues();

  var rowJournal = 0;
  var rowSummary = 0;
  var is_header = true;

  var stmtJournal = conn.prepareStatement("insert into " + JOURNAL_TABLE
    + " (biz_line, batch_ref, trans_date, trans_type, trans_subtype1, trans_subtype2, "
    + "trans_biz_loc, trans_amount_php) values(?,?,?,?,?,?,?,?);");
  var stmtSummary = conn.prepareStatement("insert into import_daily_summary "
    + "(batch_ref, trans_date, biz_loc, trans_type, trans_subtype1, trans_subtype2, day_total) "
    + "values(?,?,?,?,?,?,?);");

  for (var row in values) {
    if (is_header) {
      is_header = false;
    }
    else {
      if ((values[row][SUMMARY_DAY_TOTAL] * 1) != 0) {
        stmtSummary.setString(1, batchRef);
        stmtSummary.setObject(2, batchDate);
        stmtSummary.setString(3, values[row][SUMMARY_BIZ_LOC]);
        stmtSummary.setString(4, values[row][SUMMARY_TRANS_TYPE]);
        if (values[row][SUMMARY_TRANS_SUBTYPE1] == "") { stmtSummary.setNull(5, NULL_VARCHAR) }
        else { stmtSummary.setString(5, values[row][SUMMARY_TRANS_SUBTYPE1]) }
        if (values[row][SUMMARY_TRANS_SUBTYPE2] == "") { stmtSummary.setNull(6, NULL_VARCHAR) }
        else { stmtSummary.setString(6, values[row][SUMMARY_TRANS_SUBTYPE2]) }
        if (values[row][SUMMARY_DAY_TOTAL] == "") { stmtSummary.setDouble(7, 0) }
        else { stmtSummary.setDouble(7, values[row][SUMMARY_DAY_TOTAL]) }
        stmtSummary.addBatch();
        rowSummary++;

        transFullType = values[row][SUMMARY_TRANS_TYPE] + ":"
          + values[row][SUMMARY_TRANS_SUBTYPE1] + ":" + values[row][SUMMARY_TRANS_SUBTYPE2];
        if (transFullType != "Income:Rental:Rental" && transFullType != "Income:Retail Sale:Retail Sale") {
          stmtJournal.setString(1, BIZ_LINE);
          stmtJournal.setString(2, batchRef);
          stmtJournal.setObject(3, batchDate);
          stmtJournal.setString(4, values[row][SUMMARY_TRANS_TYPE]);
          stmtJournal.setString(5, values[row][SUMMARY_TRANS_SUBTYPE1]);
          stmtJournal.setString(6, values[row][SUMMARY_TRANS_SUBTYPE2]);
          stmtJournal.setString(7, values[row][SUMMARY_BIZ_LOC]);
          stmtJournal.setDouble(8, values[row][SUMMARY_DAY_TOTAL]);
          stmtJournal.addBatch();
          rowJournal++;
        }
      }
    }
  }

  if (rowSummary > 0) {
    stmtSummary.executeBatch();
  }
  if (rowJournal > 0) {
    stmtJournal.executeBatch();
  }
  stmtSummary.close();
  stmtJournal.close();
}

function staff_name(id) {
  if (id) {
    var cn = Jdbc.getConnection(URL, "horace", "Luv!270211");
    var stmt = cn.createStatement();
    var rs = stmt.executeQuery("select staff_alias from staff where staff_id = " + id + ";")
    if (rs.next()) {
      return rs.getString(1);
    } else {
      return "*Not found*";
    }
  }
}

function receipt_exists(key) {
  if (key == "") {
    return "";
  } else {
    var cn = Jdbc.getConnection(URL, "horace", "Luv!270211");
    var stmt = cn.createStatement();
    var rs = stmt.executeQuery("select * from client_receipt where receipt_number = '" + key.trim() + "';")
    if (rs.next()) {
      return "Y";
    } else {
      return "N";
    }
  }
}

function query_receipt(key) {
  var paid_amount;

  if (key == "") {
    return "";
  } else {
    var cn = Jdbc.getConnection(URL, "horace", "Luv!270211");
    var stmt = cn.createStatement();
    var rs = stmt.executeQuery("select trans_biz_loc, staff_id, coordinator_name, client_names, " +
      "event_date, receipt_amount_php, unpaid_balance_php, is_final from client_receipt " +
      "where receipt_number = '" + key.trim() + "';");
    if (rs.next()) {
      paid_amount = 1 * rs.getDouble(6) - rs.getDouble(7)
      return rs.getString(1) + "\n" +
        rs.getBoolean(8) + "\n" +
        // rs.getString(5) + "\n" +
        Utilities.formatDate(new Date(rs.getString(5)), "GMT+8", "dd-MMM-yyyy") + "\n" +
        rs.getString(3) + "\n" +
        rs.getString(4) + "\n" +
        rs.getDouble(6) + "\n" +
        paid_amount + "\n" +
        rs.getDouble(7);
    } else {
      return "*Not found*";
    }
  }
}

function test1() {
  var a = 1;
  Logger.log(test2(a));
  Logger.log(a);
}

function test2(b) {
  b = 2;
  return 3;
}

function test3() {
  conn = Jdbc.getConnection(URL, "horace", "");
  var stmtReadReceipt = conn.createStatement();
  receiptDetails = stmtReadReceipt.executeQuery("select coordinator_name, client_names, "
    + "event_date, receipt_amount_php, last_amend_date, unpaid_balance_php "
    + "from client_receipt");
  if (receiptDetails.next()) {
    Logger.log(receiptDetails.getString(5));
  }
  stmtReadReceipt.close();
  conn.close();
}
