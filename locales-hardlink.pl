#!/usr/bin/perl
# replace all identical files with hard links.
# script from Alastair McKinstry, 2000-07-03

@files = `find $ARGV[0] -type f -a -not -name "LC_C*" `;

foreach $fi (@files) {
  chop ($fi);
  ($sum,$name) = split(/ /,`md5sum -b  $fi`);
  if (  $orig{$sum} eq "" ) {
    $orig{$sum} =$fi;
  } else {
    `ln -f $orig{$sum} $fi`;
  }
}
