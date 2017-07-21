#!/usr/bin/perl -w

use strict;
use warnings;
use POSIX;
use File::Pid;
use Config::Simple;
use Try::Tiny;

# make "mydaemon.log" file in /var/log/ with "chown root:adm mydaemon"
# TODO: change "mydaemon" to the exact name of your daemon.
my $daemonName    = "doc-e";
my $dieNow        = 0;                                     # used for "infinte loop" construct - allows daemon mode to gracefully exit
my $dieNowChild   = 0;
my $sleepMainLoop = 120;                                    # number of seconds to wait between "do something" execution after queue is clear
my $logging       = 1;                                     # 1= logging is on
my $logFilePath   = "/var/log/";                           # log file path
my $logFile       = $logFilePath . $daemonName . ".log";
my $pidFilePath   = "/var/run/";                           # PID file path
my $pidFile       = $pidFilePath . $daemonName . ".pid";

# ABILITAZIONE LOG SU FILE

if ($logging) {                         
	open LOG, ">>$logFile";
	select((select(LOG), $|=1)[0]); # make the log file "hot" - turn off buffering
}

print LOG "DOC-E Parent PROCESS STARTED\n";
my $cfg = new Config::Simple(filename=>"config.ini");
try{
    my $cfg_privacy = $cfg->param(-block=>"privacy");
    my $cfg_consenso = $cfg->param(-block=>"consenso");
    my $cfg_fidelity = $cfg->param(-block=>"fidelity");
    my $cfg_delega = $cfg->param(-block=>"delega");
    #print LOG $cfg_privacy->{watchdog_dirpath};
}catch{
    print LOG "Error CFG Config::Simple $_";
};

# daemonize
use POSIX qw(setsid);
chdir '/';
umask 0;
open STDIN,  '/dev/null'   or die "Can't read /dev/null: $!";
open STDOUT, '>>/dev/null' or die "Can't write to /dev/null: $!";
open STDERR, '>>/dev/null' or die "Can't write to /dev/null: $!";
defined( my $pid = fork ) or die "Can't fork: $!";
exit if $pid;
 
# dissociate this process from the controlling terminal that started it and stop being part
# of whatever process group this process was a part of.
POSIX::setsid() or die "Can't start a new session.";
 
# callback signal handler for signals.
$SIG{INT} = $SIG{TERM} = $SIG{HUP} = \&signalHandler;
$SIG{CHLD} = \&signalHandlerChild;
$SIG{PIPE} = 'ignore';
 
# create pid file in /var/run/
my $pidfile = File::Pid->new( { file => $pidFile, } );
$pidfile->write or die "Can't write PID file, /dev/null: $!";
 
logEntry("Inizio procedura lancio");
my $n = 3;
my $forks = 0;
#my $forks_watchdog[0]="";
#my $forks_watchdog[1]="";
#my $forks_watchdog[2]="";
# FORK child 

for (1 .. $n) {
  my $pid = fork;
  if (not defined $pid) {
     warn 'Could not fork';
     next;
  }
 if ($pid) {
    $forks++;
    logEntry("In the parent process PID ($$), Child pid: $pid Num of fork child processes: $forks");
    #Parent
  } else {
    #CHILD PROCESS    
    logEntry("In the child process PID ($$)"); 
    sleep 2;
    #run hook
    my $cmd="hook1.pl";
    logEntry("Run Hook number PID ($$)");
    while(){
            sleep 60;
            logEntry("While true Hook number PID ($$)");
            
    }
    exit;
    }
}

#PARENT
#for (1 .. $forks) {
#  my $pid = wait();
#  logEntry ("Parent saw $pid exiting");
#}

my $i=1;
while (($i <= $forks)&&(!$dieNow)) {
      $pid = wait();
      logEntry ("Parent saw $pid exiting");
      if ($dieNow){
      logEntry ("Catch Signal Stop PARENT");
      }
      $i++;
}

logEntry ("Parent ($$) ending");

# add a line to the log file
sub logEntry {
	my ($logText) = @_;
	my ( $sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst ) = localtime(time);
	my $dateTime = sprintf "%4d-%02d-%02d %02d:%02d:%02d", $year + 1900, $mon + 1, $mday, $hour, $min, $sec;
	if ($logging) {
		print LOG "$dateTime $logText\n";
	}
}
 
# catch signals and end the program if one is caught.
sub signalHandler {
	logEntry("Handler Signal STOP");
  $dieNow = 1;
  $dieNowChild = 1;
}

sub signalHandlerChild {
	logEntry("Handler Signal STOP CHILD ");
  $dieNowChild = 1;
}
 
# do this stuff when exit() is called.
END {
	if ($logging) { close LOG }
	$pidfile->remove if defined $pidfile;
}