#!/bin/bash
# Slack Format Filter
# Converts *italic* to **bold** for Slack messages.
# Preserves **bold**, code spans, and list markers.
#
# Usage: echo "message" | ./slack_format.sh
#   OR:  ./slack_format.sh < input.txt
#   OR:  cat message.txt | ./slack_format.sh

perl -pe '
  # Split on code spans to protect backtick content
  my $out = "";
  my @parts = split /(`[^`]*`)/, $_;
  for my $p (@parts) {
    if ($p =~ /^`/) {
      $out .= $p;                # code span — untouched
    } else {
      # *italic* -> **bold** (single asterisk wrapping, not double)
      1 while $p =~ s/(?<!\*)\*([^*\*]+)\*(?!\*)/**\1**/g;
      $out .= $p;
    }
  }
  $_ = $out;
' | cat -s
