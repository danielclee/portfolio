<?php

require_once('ParseTxtFileBaseClass.php');

/**
 * CLASS ParseCurrentContentRev1
 **/
class ParseCurrentContentRev1 extends ParseTxtFileBaseClass
{
  // CLASS CONSTANTS

  const REVISION_NUMBER              = 1;
  const VAULT_DROP                   = 0;
  const RESERVE_CHANGE_FUND          = 1;
  const COURIER_TRAY                 = 2;

  // CLASS VARIABLES

  // CLASS FUNCTIONS

  /**********************************************************************
   * SetupParsingInfo
   **********************************************************************/
  protected function SetupParsingInfo()
  {
    $this->PregMatchLut = 
     array('/^For Store: [a-zA-Z0-9\/\s]+/' => 'ParseCurrentContentRev1::ParseStoreId',
           '/^Printed on [0-9]+\/[0-9]+\/[0-9]+ [0-9]+:[0-9]+ .M/' => 'ParseCurrentContentRev1::ParseDate',
           '/^Revision [0-9]+/' => 'ParseCurrentContentRev1::ParseRevision',
           '/^Current Vault Drop$/' => 'ParseCurrentContentRev1::ParseVaultDrop',
           '/^Current Reserve Change Fund$/' => 'ParseCurrentContentRev1::ParseCurrentReserveFund',
           '/^Current Courier Tray$/' => 'ParseCurrentContentRev1::CurrentCourierTray',
           '/^BILL ACCEPTOR CONTENTS$/' => 'ParseCurrentContentRev1::ParseBillAcpDenomCounts',
           '/^Total$/' => 'ParseCurrentContentRev1::ParseBillAcpTotals',
           '/^GRAND TOTAL:[ ]+[0-9]+\.[0-9]+/' => 'ParseCurrentContentRev1::ParseGrandTotal',
           );
  }

  /**********************************************************************
   * ParseStoreId
   **********************************************************************/
  protected function ParseStoreId($matches)
  {
    $tokens = preg_split("/[ ]+/", $matches);
    echo "store_id (" . trim($tokens[2]) . ")<br>";
    echo "store_id2 (" . trim($tokens[6]) . ")<br>";
  }

  /**********************************************************************
   * ParseRevision
   **********************************************************************/
  protected function ParseRevision($matches)
  {
    $rev = $this->getTokenPos(" ", 1, $matches);
    if ((int)$rev <= self::REVISION_NUMBER)
    {
      echo "ParseCourierPickupRev1 cannot parse this revision ($rev) <br>";
      $this->abort = true;
    }
    echo "courier_pickup_revision ($rev) <br>";
  }

  /**********************************************************************
   * ParseDate
   **********************************************************************/
  protected function ParseDate($matches)
  {
    $date = $this->getTokenPos(" ", 2, $matches);
    $time = $this->getTokenPos(" ", 3, $matches);
    echo "current_content_datetime (" . $date . "  " . $time . ") <br>";
  }

  /**********************************************************************
   * ParseGrandTotal
   **********************************************************************/
  protected function ParseGrandTotal($matches)
  {
      $tokens = preg_split("/[ ]+/", $matches);
      echo "grand_total (" . trim($tokens[2]) . ")<br>";
  }

  /**********************************************************************
   * ParseVaultDrop
   **********************************************************************/
  protected function ParseVaultDrop($matches)
  {
    $this->ParseCurrentCounts(self::VAULT_DROP);
  }

  /**********************************************************************
   * ParseCurrentReserveFund
   **********************************************************************/
  protected function ParseCurrentReserveFund($matches)
  {
    $this->ParseCurrentCounts(self::RESERVE_CHANGE_FUND);
  }

  /**********************************************************************
   * CurrentCourierTray
   **********************************************************************/
  protected function CurrentCourierTray($matches)
  {
    $this->ParseCurrentCounts(self::COURIER_TRAY);
  }

  /**********************************************************************
   * parseCurrentCounts
   **********************************************************************/
  private function ParseCurrentCounts($type)
  {
    echo "Current count type ($type) <br>";

    $loopsafe = 0;
    $this->fileBufferArrayItor->next(); 
    while(($this->fileBufferArrayItor->valid()) && ($loopsafe<4))
    {
      // Get line data
      $line = $this->fileBufferArrayItor->current();
      if (preg_match('/^[ ]+\(Cash\)/', $line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $line);
        echo "cash ($tokens[2]) <br>";
      }
      else if (preg_match('/^[ ]+\(Check\)/', $line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $line);
        echo "check ($tokens[2]) <br>";
      }
      else if (preg_match('/^[ ]+\(Total\)/', $line, $matches) == 1)
      {
        $tokens = preg_split("/[ ]+/", $line);
        echo "total ($tokens[2]) <br>";
        break;
      }

      $loopsafe++;
      $this->fileBufferArrayItor->next();  // get next line
    }
  }
} /* End ParseCurrentContentRev1 */
?>
