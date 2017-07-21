#!/usr/bin/perl -w

@files = <*>;
foreach $file (@files) {
  print $file . "\n";
}
