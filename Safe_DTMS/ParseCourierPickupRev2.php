<?php

require_once('ParseTxtFileBaseClass.php');

/**
 * CLASS ParseCourierPickupRev2
 **/
class ParseCourierPickupRev2 extends ParseTxtFileBaseClass
{
  // CLASS CONSTANTS

  const REVISION_NUMBER               = 2;
  const PARTIAL_DAY_BREAKDOWN         = 0;
  const PARTIAL_DAY_UP_TO_BREAKDOWN   = 1;
  const BUSINESS_DAY_BREAKDOWN        = 2;

  // CLASS VARIABLES

  private $datetime;
  private $sdaterange;
  private $edaterange;

  // CLASS FUNCTIONS

  /**********************************************************************
   * Ctor
   **********************************************************************/
  public function __construct($filepath)
  {
    parent::__construct($filepath);

    // Initialize variables
    $this->sdaterange = "";
    $this->edaterange = "";

    // Parse datetime from filename

    $myArray = explode("_", $filepath);
    if (!is_array($myArray) || sizeof($myArray) == 0)
    {
      $this->DebugOutput("ParseCourierPickupRev2 : " . 
                         "Error parsing datetime");
      return;
    }

    // datetime is the last entry
    $this->datetime = $myArray[sizeof($myArray)-1];
    $this->datetime = substr($this->datetime, 0, 8) . 
                      " " . substr($this->datetime, 8, 8);      
    $this->datetime = strtotime($this->datetime);
    $this->datetime = date("Y-m-d H:i:s", $this->datetime);      

    // Get safe ID

    $myArray = pathinfo($filepath);
    if (!is_array($myArray) || sizeof($myArray) == 0)
    {
      $this->DebugOutput("ParseCourierPickupRev2 : " . 
                         "Error parsing safe ID");
      return;
    }
    $myArray2 = explode("_", $myArray['basename']);
    $safeidname = $myArray2[0];
    $this->safeidFK = 
       $this->ExecuteDBCmd("SELECT safeidPK FROM safe WHERE name='$safeidname'");

$this->safeidFK = 1;  ////3434 REMOVE HACK

    unset($myArray);
    unset($myArray2);
  }

  /**********************************************************************
   * SetupParsingInfo
   **********************************************************************/
  protected function SetupParsingInfo()
  {
    $this->DEBUG = 1;

    $this->PregMatchLut = 
     array('/^[0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseCourierPickupRev2::ParseDateInterval',
           '/^Revision [0-9]+/' => 'ParseCourierPickupRev2::ParseRevision',
           '/^Total value of pickup \$[0-9]+\.[0-9]+/' => 'ParseCourierPickupRev2::ParseTotalPickupValue',
           '/in the courier tray/' => 'ParseCourierPickupRev2::ParseTrayCashContents',
           '/in the courier tray/' => 'ParseCourierPickupRev2::ParseTrayCheckContents',
           '/^BILL ACCEPTOR COUNTS$/' => 'ParseCourierPickupRev2::ParseBillAcpDenomCounts',
           '/^Total$/' => 'ParseCourierPickupRev2::ParseBillAcpTotals',
           '/^Partial day ending [0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseCourierPickupRev2::ParsePartialDayBreakdown',
           '/^Business day ending [0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseCourierPickupRev2::ParseBusinessDayBreakdown',
           '/^Partial day up to [0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseCourierPickupRev2::ParsePartialDayUpToBreakdown',
           );
  }

  /**********************************************************************
   * ParseRevision
   **********************************************************************/
  protected function ParseRevision($matches)
  {
    $rev = $this->getTokenPos(" ", 1, $matches);
    if ((int)$rev > self::REVISION_NUMBER)
    {
      echo "ParseCourierPickupRev2 cannot parse this revision ($rev) <br>";
      $this->abort = true;
    }
  }

  /**********************************************************************
   * ParseDateInterval
   **********************************************************************/
  protected function ParseDateInterval($matches)
  {
    static $enddatefound = false;

    $date = $this->getTokenPos(" ", 0, $matches);
    $time = $this->getTokenPos(" ", 1, $matches);
    $timem = $this->getTokenPos(" ", 2, $matches);

    if (!$enddatefound)
    {
      $this->sdaterange = "$date $time $timem";
      $this->sdaterange = strtotime($this->sdaterange);
      $this->sdaterange = date("Y-m-d H:i:s", $this->sdaterange);      
      $this->DebugOutput("ParseCourierPickupRev2 : " . 
                         "Timestamp start ($this->sdaterange)");
      $enddatefound = true;
    }
    else
    {
      $this->edaterange = "$date $time $timem";
      $this->edaterange = strtotime($this->edaterange);
      $this->edaterange = date("Y-m-d H:i:s", $this->edaterange);      
      $this->DebugOutput("ParseCourierPickupRev2 : " . 
                         "Timestamp end ($this->edaterange)");
    }
  }

  /**********************************************************************
   * ParseTotalPickupValue
   **********************************************************************/
  protected function ParseTotalPickupValue($matches)
  {
    $total = $this->getTokenPos(" ", 4, $matches);
    $this->DebugOutput(
             "ParseCourierPickupRev2 : Total pickup value ($total)");
    $this->ExecuteDBCmd("INSERT INTO safe_courier_pickup_total " . 
                        "(safeidFK,total_pickup,sdatetime,edatetime) " . 
                        "VALUES ($this->safeidFK,$total," . 
                        "$this->sdaterange,$this->edaterange)");
  }

  /**********************************************************************
   * ParseTrayCashContents
   **********************************************************************/
  protected function ParseTrayCashContents($matches)
  {
  }

  /**********************************************************************
   * ParseTrayCheckContents
   **********************************************************************/
  protected function ParseTrayCheckContents($matches)
  {
  }

  /**********************************************************************
   * ParseDenom5Entry
   **********************************************************************/
  protected function ParseDenom5Entry($denomline) 
  {
    $tokens = preg_split("/[ ]+/", trim($denomline));

    if ((trim($tokens[0]) == "All") || (trim($tokens[0]) == "Value"))
      return;

    if (sizeof($tokens) == 5)
    {
      $denom = str_replace('$', '', trim($tokens[0]));
      $billval1 = trim($tokens[1]);
      $billval2 = trim($tokens[2]);
      $total = trim($tokens[3]);
      $value = str_replace('$', '', trim($tokens[4]));

      // Insert denom

      if ((int)$denom > 0)
      {
        $this->DebugOutput("ParseCourierPickupRev2 : Denom (\$$denom) " . 
                           "Billval 1 ($billval1) Billval 2 ($billval2) " . 
                           "Total ($total) Value (\$$value)");

        // Insert denom
        $denomId = $this->ExecuteDBCmd("INSERT IGNORE INTO safe_bill_denom " . 
                                       "(denom) VALUES ($denom)");

$denomId = 1; //3434 REMOVE HACK

        // Make sure (denom count * denom) is same as value
  
        if (((int)$denom * (int)$total) != (int)$value)
          $this->DebugOutput("ParseCourierPickupRev2 : " . 
                             "Error denom count formula error");
  
        // Insert denom data
        $this->ExecuteDBCmd("INSERT INTO safe_courier_pickup_denom_data " . 
         "(safeidFK,denomFK,billval1,billval2,count,value,sdatetime,edatetime) " . 
         "VALUES ($this->safeidFK,$denomId,$billval1,$billval2,$total,$value," . 
         "$this->sdaterange,$this->edaterange)");
      }
    }
  }

  /**********************************************************************
   * ParsePartialDayBreakdown
   **********************************************************************/
  protected function ParsePartialDayBreakdown($matches)
  {
    // Get datetime

    $date = $this->getTokenPos(" ", 3, $matches);
    $time = $this->getTokenPos(" ", 4, $matches);
    $timem = $this->getTokenPos(" ", 5, $matches);
    $sqldatetime = "$date $time $timem";
    $sqldatetime = strtotime($sqldatetime);
    $sqldatetime = date("Y-m-d H:i:s", $sqldatetime);      

    $this->ParseBusinessBreakdownEntry(self::PARTIAL_DAY_BREAKDOWN,
                                       $sqldatetime);
  }

  /**********************************************************************
   * ParseBusinessDayBreakdown
   **********************************************************************/
  protected function ParseBusinessDayBreakdown($matches)
  {
    // Get datetime

    $date = $this->getTokenPos(" ", 3, $matches);
    $time = $this->getTokenPos(" ", 4, $matches);
    $timem = $this->getTokenPos(" ", 5, $matches);
    $sqldatetime = "$date $time $timem";
    $sqldatetime = strtotime($sqldatetime);
    $sqldatetime = date("Y-m-d H:i:s", $sqldatetime);      

    $this->ParseBusinessBreakdownEntry(self::BUSINESS_DAY_BREAKDOWN,
                                       $sqldatetime);
  }

  /**********************************************************************
   * ParsePartialDayUpToBreakdown
   **********************************************************************/
  protected function ParsePartialDayUpToBreakdown($matches)
  {
    // Get datetime

    $date = $this->getTokenPos(" ", 4, $matches);
    $time = $this->getTokenPos(" ", 5, $matches);
    $timem = $this->getTokenPos(" ", 6, $matches);
    $sqldatetime = "$date $time $timem";
    $sqldatetime = strtotime($sqldatetime);
    $sqldatetime = date("Y-m-d H:i:s", $sqldatetime);      

    $this->ParseBusinessBreakdownEntry(self::PARTIAL_DAY_UP_TO_BREAKDOWN,
                                       $sqldatetime);
  }

  /**********************************************************************
   * ParseBusinessBreakdownEntry
   **********************************************************************/
  private function ParseBusinessBreakdownEntry($type, $sqldatetime)
  {
    $breakacpcash = "";
    $breakcashdeposit = "";
    $breakcheckdeposit = "";
    $breaktotaldeposit = "";
    
    $this->DebugOutput("ParseCourierPickupRev2 : Business day " . 
                       "breakdown type ($type) timestamp ($sqldatetime)");

    // Parse lines

    static $bdowntype = -1;
    switch ($type)
    {
      case self::PARTIAL_DAY_BREAKDOWN:
        if ($bdowntype != self::PARTIAL_DAY_BREAKDOWN)
        {
          $bdowntype = $this->ExecuteDBCmd(
              "INSERT IGNORE INTO safe_breakdown_type (breakdowntypePK,name) VALUES " . 
              "($type,'partial_day_breakdown')");
        }
        break;

      case self::PARTIAL_DAY_UP_TO_BREAKDOWN:
        if ($bdowntype != self::PARTIAL_DAY_UP_TO_BREAKDOWN)
        {
          $bdowntype = $this->ExecuteDBCmd(
           "INSERT IGNORE INTO safe_breakdown_type (breakdowntypePK,name) VALUES " . 
           "($type,'partial_day_upto_breakdown')");
        }
        break;

      case self::BUSINESS_DAY_BREAKDOWN:
        if ($bdowntype != self::BUSINESS_DAY_BREAKDOWN)
        {
          $bdowntype = $this->ExecuteDBCmd(
           "INSERT IGNORE INTO safe_breakdown_type (breakdowntypePK,name) VALUES " . 
           "($type,'business_day_breakdown')");
        }
        break;

      default:
        $this->DebugOutput("ParseCourierPickupRev2 : " . 
                           "Unknown breakdown type detected");
        break;
    };

    $loopsafe = 0;
    $this->fileBufferArrayItor->next(); 
    while(($this->fileBufferArrayItor->valid()) && ($loopsafe<6))
    {
      // Get line data
      $this->line = $this->fileBufferArrayItor->current();

      if (preg_match('/^Acceptor cash/', $this->line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $this->line);
        $breakacpcash = str_replace('$', '', trim($tokens[2]));
      }
      else if (preg_match('/^Courier tray cash deposits/', $this->line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $this->line);
        $breakcashdeposit = str_replace('$', '', trim($tokens[4]));
      }
      else if (preg_match('/^Courier tray check deposits/', $this->line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $this->line);
        $breakcheckdeposit = str_replace('$', '', trim($tokens[4]));
      }
      else if (preg_match('/^Total deposit value/', $this->line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $this->line);
        $breaktotaldeposit = str_replace('$', '', trim($tokens[3]));
        break;
      }

      $loopsafe++;
      $this->fileBufferArrayItor->next();  // get next line
    }

    // Insert into db

    $this->ExecuteDBCmd("INSERT INTO safe_courier_pickup_breakdown " . 
       "(safeidFK,breakdownTypeFK,billval_cash,cash_deposit," . 
       "check_deposit,total,timestamp,sdatetime,edatetime) " . 
       "VALUES ($this->safeidFK,$type,$breakacpcash,$breakcashdeposit," . 
       "$breakcheckdeposit,$breaktotaldeposit,$sqldatetime," . 
       "$this->sdaterange,$this->edaterange)");
  }
} /* End ParseCourierPickupRev2 */
?>
