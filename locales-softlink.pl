#!/usr/bin/perl
# make LC_CTYPE and LC_COLLATE symlinks

@files = `find [A-Z]* $ARGV[0]* -type f -a -name "LC_C*" `;

foreach $fi (@files) {
  chop ($fi);
  ($sum,$name) = split(/ /,`md5sum -b  $fi`);
  if (  $orig{$sum} eq "" ) {
    $orig{$sum} =$fi;
  } else {
    `rm $fi`;
    `ln -s ../$orig{$sum} $fi`;
  }
}
