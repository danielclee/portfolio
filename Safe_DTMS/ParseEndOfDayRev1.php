<?php

require_once('ParseTxtFileBaseClass.php');

/**
 * CLASS ParseEndOfDayRev1
 **/
class ParseEndOfDayRev1 extends ParseTxtFileBaseClass
{
  // CLASS CONSTANTS

  const REVISION_NUMBER              = 1;
  const VAULT_DROP                   = 0;
  const RESERVE_CHANGE_FUND          = 1;
  const COURIER_TRAY                 = 2;

  // CLASS VARIABLES

  private $datetime;
  private $currentShiftId;

  // CLASS FUNCTIONS

  /**********************************************************************
   * SetupParsingInfo
   **********************************************************************/
  protected function SetupParsingInfo()
  {
    $this->DEBUG = 1;

    $this->datetime = "";
    $this->currentShiftId = "";

    $this->PregMatchLut = 
      array('/^For Store: [a-zA-Z0-9\/\s]+/' => 'ParseEndOfDayRev1::ParseStoreId',
            '/^Printed on [0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseEndOfDayRev1::ParseDate',
            '/^[0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseEndOfDayRev1::ParseDateInterval',
            '/^Revision [0-9]+/' => 'ParseEndOfDayRev1::ParseRevision',
            '/^Bills Accepted:[\s]+[0-9]+.[0-9]/' => 'ParseEndOfDayRev1::ParseBillsAccepted',
            '/^Total Vault Drops:[\s]+[0-9]+.[0-9]/' => 'ParseEndOfDayRev1::ParseVaultDrops',
            '/^Total Bills \+ Drops:[\s]+[0-9]+.[0-9]/' => 'ParseEndOfDayRev1::ParseTotalBillsDrops',
            '/^Courier Tray Deposits$/' => 'ParseEndOfDayRev1::ParseCourierTrayDeposits',
            '/^Current Reserve Change Fund Contents$/' => 'ParseEndOfDayRev1::ParseCurrentReserveChangeFundContents',
            '/^SHIFT_[0-9]$/' => 'ParseEndOfDayRev1::ParseShiftData',
           );
  }

  /**********************************************************************
   * PostParsing
   **********************************************************************/
  protected function PostParsing() 
  {
  }

  /**********************************************************************
   * ParseStoreId
   **********************************************************************/
  protected function ParseStoreId($matches)
  {
    $this->safeidFK = 0;

    $tokens = preg_split("/[ ]+/", $matches);
    $safeidname = trim($tokens[2]);
    $this->safeidFK = 
       $this->ExecuteDBCmd("SELECT safeidPK FROM safe WHERE name='$safeidname'");

$this->safeidFK = 1;  //3434 HACK

    if ((int)$this->safeidFK == 0)
    {
      $this->DebugOutput("ParseEndOfDayRev1 : Invalid safe ID ($this->safeidFK)");
      $this->abort = true;
    }
    $this->DebugOutput("ParseEndOfDayRev1 : Store ID ($this->safeidFK)");
  }

  /**********************************************************************
   * ParseDate
   **********************************************************************/
  protected function ParseDate($matches)
  {
  }

  /**********************************************************************
   * ParseDateInterval
   **********************************************************************/
  protected function ParseDateInterval($matches) 
  {
    static $enddatefound = false;

    if (!$enddatefound)
    {
      $enddatefound = true;
    }
    else
    {
      $date = $this->getTokenPos(" ", 0, $matches);
      $time = $this->getTokenPos(" ", 1, $matches);
      $timem = $this->getTokenPos(" ", 2, $matches);

      $this->datetime = "$date $time $timem";
      $this->datetime = strtotime($this->datetime);
      $this->datetime = date("Y-m-d H:i:s", $this->datetime);
      $this->DebugOutput("ParseEndOfDayRev1 : Timestamp ($this->datetime)");
    }
  }

  /**********************************************************************
   * ParseRevision
   **********************************************************************/
  protected function ParseRevision($matches)
  {
    $rev = $this->getTokenPos(" ", 1, $matches);
    if ((int)$rev > self::REVISION_NUMBER)
    {
      echo "ParseEndOfDayRev1 : Cannot parse this revision ($rev) <br>";
      $this->abort = true;
    }
    $this->DebugOutput("ParseEndOfDayRev1 : Revision ($rev)");
  }

  /**********************************************************************
   * ParseBillsAccepted
   **********************************************************************/
  protected function ParseBillsAccepted($matches)
  {
    $tokens = preg_split("/[ ]+/", $matches);
    $totalBillsAccepted = trim($tokens[2]);
    $this->DebugOutput(
             "ParseEndOfDayRev1 : Bills accepted ($totalBillsAccepted)");
    $this->ExecuteDBCmd("INSERT INTO safe_bills_accepted " . 
                        "(safeidFK,total_bills_accepted,datetime) " . 
                        "VALUES ($this->safeidFK,$totalBillsAccepted," . 
                        "$this->datetime)");
  }

  /**********************************************************************
   * ParseVaultDrops
   **********************************************************************/
  protected function ParseVaultDrops($matches)
  {
    $tokens = preg_split("/[ ]+/", $matches);
    $totalVaultDrops = trim($tokens[3]);
    $this->DebugOutput(
                  "ParseEndOfDayRev1 : Vault drops ($totalVaultDrops)");
    $this->ExecuteDBCmd("INSERT INTO safe_vault_drops " . 
                        "(safeidFK,total_vault_drops,datetime) " . 
                        "VALUES ($this->safeidFK,$totalVaultDrops," . 
                        "$this->datetime)");
  }

  /**********************************************************************
   * ParseTotalBillsDrops
   **********************************************************************/
  protected function ParseTotalBillsDrops($matches)
  {
    $tokens = preg_split("/[ ]+/", $matches);
    $totalBillsAndDrops =  trim($tokens[4]);
    $this->DebugOutput(
      "ParseEndOfDayRev1 : Total bills and drops ($totalBillsAndDrops)");
    $this->ExecuteDBCmd("INSERT INTO safe_bills_n_drops " . 
                        "(safeidFK,total_bills_n_drops,datetime) " . 
                        "VALUES ($this->safeidFK,$totalBillsAndDrops," . 
                        "$this->datetime)");
  }

  /**********************************************************************
   * ParseCourierTrayDeposits
   **********************************************************************/
  protected function ParseCourierTrayDeposits($matches)
  {
    $this->fileBufferArrayItor->next(); 
    $line = $this->fileBufferArrayItor->current();
    $tokens = preg_split("/[ ]+/", $line);
    $courierTrayDeposits = trim($tokens[3]);
    $this->DebugOutput(
      "ParseEndOfDayRev1 : Courier tray deposits ($courierTrayDeposits)");
    $this->ExecuteDBCmd("INSERT INTO safe_courier_tray_deposits " . 
                        "(safeidFK,courier_tray_deposits,datetime) " . 
                        "VALUES ($this->safeidFK,$courierTrayDeposits," . 
                        "$this->datetime)");
  }

  /**********************************************************************
   * ParseCurrentReserveChangeFundContents
   **********************************************************************/
  protected function ParseCurrentReserveChangeFundContents($matches) {}

  /**********************************************************************
   * ParseShiftData
   **********************************************************************/
  protected function ParseShiftData($matches)
  {
    // Put shift name into db

    $tokens = preg_split("/[_]+/", $matches);
    $safename = trim($tokens[1]);
    $this->DebugOutput("ParseEndOfDayRev1 : Shift ($safename)");
    $this->currentShiftId = 
              $this->ExecuteDBCmd("INSERT IGNORE INTO safe_shift " . 
                                  "(shift_name) VALUES ($safename)");
$this->currentShiftId = 1;  //3434 HACK

    // Parse through shift data

    $loopsafe = 0;
    $this->fileBufferArrayItor->next(); 
    while(($this->fileBufferArrayItor->valid()) && ($loopsafe<10))
    {
      // Get line data
      $line = $this->fileBufferArrayItor->current();

      if (preg_match('/^[ ]+BILLS ACCEPTED/', $line, $matches) == 1)  // needs to be last
      {
        $this->ParseBillAcpTotals($matches);
        break;
      }
      $loopsafe++;
      $this->fileBufferArrayItor->next();  // get next line
    }
  }

  /**********************************************************************
   * ParseDenom3Entry
   **********************************************************************/
  protected function ParseDenom3Entry($denomline) 
  {
    $tokens = preg_split("/[ ]+/", trim($denomline));

    if (trim($tokens[0]) == "All")
      return;

    if (sizeof($tokens) == 3)
    {
      $denom = str_replace('$', '', trim($tokens[0]));
      $count = trim($tokens[1]);
      $value = str_replace('$', '', trim($tokens[2]));

      // Insert denom

      if ((int)$denom > 0)
      {
        $this->DebugOutput("ParseEndOfDayRev1 : Denom (\$$denom) " . 
                           "Count ($count) Value (\$$value)");

        // Insert denom
        $denomId = $this->ExecuteDBCmd("INSERT IGNORE INTO safe_bill_denom " . 
                                       "(denom) VALUES ($denom)");

$denomId = 1; //3434 REMOVE HACK

        // Make sure (denom count * denom) is same as value
  
        if (((int)$denom * (int)$count) != (int)$value)
          $this->DebugOutput("ParseEndOfDayRev1 : Error denom count formula error");
  
        // Insert denom count and value
        $this->ExecuteDBCmd("INSERT INTO safe_shift_denom_data " . 
                            "(shiftidFK,denomFK,count,value) VALUES " . 
                            "($this->currentShiftId,$denomId,$count,$value)");
      }
    }
  }
} /* End ParseEndOfDayRev1 */
?>
