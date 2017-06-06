#!/usr/bin/perl -w

use Config::Simple;

my $cfg = new Config::Simple();
$cfg->read('config.ini'); 
my $prova=$cfg->param(-block=>"privacy");
$test = $prova->{keydoc1};
print "TEST-->".$test."\n";