<?php
/**
 * CLASS ParseTxtFileBaseClass
 **/
class ParseTxtFileBaseClass
{
  // CLASS CONSTANTS

  // CLASS VARIABLES

  protected $filePath;
  protected $fileBufferArray;
  protected $fileBufferArrayItor;
  protected $line;
  protected $PregMatchLut;
  protected $PregMatchLutObj;
  protected $abort;
  protected $safeidFK;
  protected $DEBUG;

  // CLASS FUNCTIONS

  /**********************************************************************
   * Ctor
   **********************************************************************/
  public function __construct($filepath)
  {
    $this->filePath = $filepath;
    $this->SetupParsingInfo();
    $this->abort = false;
    $this->safeidFK = 0;

    $this->DEBUG = 0;
  }

  /**********************************************************************
   * Dtor
   **********************************************************************/
  public function __destruct()
  {
  }

  /**********************************************************************
   * DebugOutput
   **********************************************************************/
  protected function DebugOutput($output)
  {
    echo $output . "<br>";
  }

  /**********************************************************************
   * ExecuteDBCmd
   **********************************************************************/
  protected function ExecuteDBCmd($dbcmd)
  {
    // Run the string contained in $dbcmd

    // DB CODE GOES HERE
    echo $dbcmd . "<br>";
  }

  /**********************************************************************
   * SetupParsingInfo
   **********************************************************************/
  protected function SetupParsingInfo() {}

  /**********************************************************************
   * ParseFile
   **********************************************************************/
  public function ParseFile()
  {
    if (empty($this->PregMatchLut))
    {
      $this->DebugOutput("Parsing $this->filePath failed, no match table set");
      return(false);
    }

    $this->DebugOutput("PARSING $this->filePath");

    // Read file into array
    $fileBufferArray = new ArrayObject(file($this->filePath));
    $this->fileBufferArrayItor = $fileBufferArray->getIterator();

    // Instantiate preg match lut
    $this->PregMatchLutObj = new ArrayObject($this->PregMatchLut);

    // Go through each line in file array and evaluate
  
    while ($this->fileBufferArrayItor->valid() && !$this->abort)
    {
      // Parse individual line
      $line = $this->fileBufferArrayItor->current();
      if (!$this->evaluatePredicate($line))
        return(false);

      // Go to the next line
      $this->fileBufferArrayItor->next();
    }

    // Call post parsing fn
    $this->PostParsing();

    unset($this->PregMatchLutObj);
    unset($this->fileBufferArrayItor);
    unset($this->fileBufferArray);

    return(true);
  }

  /**********************************************************************
   * evaluatePredicate
   **********************************************************************/
  protected function evaluatePredicate($line)
  {
    foreach($this->PregMatchLutObj as $key => $value) 
    {
      if (preg_match($key, trim($line), $matches) == 1)
      {
        if (is_callable($value))
          call_user_func_array($value, $matches);
      }
    }

    return(true);
  }

  /**********************************************************************
   * PostParsing
   **********************************************************************/
  protected function PostParsing() {}

  /**********************************************************************
   * getTokenPos
   **********************************************************************/
  protected function getTokenPos ($token, $tokenpos, $searchstr)
  {
    $tok = strtok($searchstr, $token);
    $tokidx = 0;
    while ($tok !== false) 
    {
      if ($tokidx == $tokenpos)
        return($tok);
      $tok = strtok($token);
      $tokidx++;
    }
    
    return("");
  }

  /**********************************************************************
   * ParseBillAcpCounts
   **********************************************************************/
  protected function ParseBillAcpDenomCounts($matches)
  {
    // The next line will be the column titles

    $this->fileBufferArrayItor->next(); 
    $this->line = $this->fileBufferArrayItor->current();

    // Parse the bill acceptor table

    $loopsafe = 0;
    $this->fileBufferArrayItor->next(); 
    while(($this->fileBufferArrayItor->valid()) && ($loopsafe<10))
    {
      // Get line data
      $this->line = $this->fileBufferArrayItor->current();

      if (preg_match('/^\$[0-9]+[ ]+[0-9]+[ ]+[0-9]+[ ]+[0-9]+[ ]+\$[0-9]+/', $this->line, $matches) == 1)
      {
        // Parse denomination line
        $this->ParseDenom5Entry($this->line);
      }
      else if (preg_match('/^All[ ]+[0-9]+[ ]+[0-9]+[ ]+[0-9]+/', $this->line, $matches) == 1)  // needs to be last
      {
        // Parse denomination line
        $this->ParseDenom5Entry($this->line);
      }
      else if (preg_match('/^Value[ ]+[0-9]+[ ]+[0-9]+[ ]+\$[0-9]+/', $this->line, $matches) == 1)  // needs to be last
      {
        // Parse denomination line
        $this->ParseDenom5Entry($this->line);
        break;
      }
      $loopsafe++;
      $this->fileBufferArrayItor->next();  // get next line
    }
  }

  /**********************************************************************
   * parseBillAcpTotals
   **********************************************************************/
  protected function ParseBillAcpTotals($matches)
  {
    // The next line will be the column titles

    $this->fileBufferArrayItor->next(); 
    $this->line = $this->fileBufferArrayItor->current();

    // Parse the bill acceptor totals table

    $loopsafe = 0;
    $this->fileBufferArrayItor->next(); 
    while(($this->fileBufferArrayItor->valid()) && ($loopsafe<10))
    {
      // Get line data
      $this->line = $this->fileBufferArrayItor->current();

      if (preg_match('/^\$[0-9]+[ ]+[0-9]+[ ]+\$[0-9]+/', trim($this->line), $matches) == 1)
      {
        // Parse denomination line
        $this->ParseDenom3Entry($this->line);
      }
      else if (preg_match('/^All[ ]+[0-9]+[ ]+\$[0-9]+/', trim($this->line), $matches) == 1)  // needs to be last
      {
        // Parse denomination line
        $this->ParseDenom3Entry($this->line);
        break;
      }
      $loopsafe++;
      $this->fileBufferArrayItor->next();  // get next line
    }
  }

  /**********************************************************************
   * ParseDenom3Entry
   **********************************************************************/
  protected function ParseDenom3Entry($denomline) {}

  /**********************************************************************
   * ParseDenom5Entry
   **********************************************************************/
  protected function ParseDenom5Entry($denomline) {}

} /* End ParseTxtFileBaseClass */
?>
