# Cisco2960SW-Automation

This project has been developed using Python to automate switch configuration. You can do automatic configuration tasks by using commands obtained from your own config file.

# Features

- Read the commands from the config file and send them automatically to the switch.
- Send commands to the terminal via the serial port using the Serial library without the need for SSH and Telnet configuration.

# How to use

1. Arrange the switch configuration commands in the config.txt listing them one after another.
2. Attempt to establish a terminal connection using the COM port with PuTTY or SecureCRT and if your successful connection is through a specific serial port, such as COM5, enter this addres as input.
3. Before running the program, please close actively running programs such as PuTTY and SecureCRT.
4. Copy your config.txt file to the project's directory

# Contributions

Pull requests are welcome. For major changes, please open an issue to discuss the proposed changes before making them.

# License

This project is licensed under the MIT License.

#!/usr/bin/env bash
# =============================================================================
# bounty-recon.sh — One-shot HTTPS-focused recon pipeline for Bug Bounty hunters
# Author  : Ferhad (generated with ChatGPT) • v0.3 • 2025-07-02
# =============================================================================
# WHAT’S NEW (v0.3)
#   • Tümüyle pasif enum: Aktif brute-force (shuffledns) & wordlist kaldırıldı
#   • Subjack entegrasyonu → potansiyel subdomain takeover tespiti
#   • Flag seti sadeleşti (-t, --depth, --nuclei, --shot)
#   • shuffledns bağımlılığı çıkarıldı, subjack eklendi
# =============================================================================
set -Eeuo pipefail
shopt -s lastpipe

# ---------- ANSI Colors -------------------------------------------------------
C0="\033[0m"; C1="\033[1;32m"; C2="\033[1;33m"; C3="\033[1;31m"; C4="\033[1;34m"
info(){ echo -e "${C1}[i]${C0} $1"; }
warn(){ echo -e "${C2}[!]${C0} $1"; }
fail(){ echo -e "${C3}[×]${C0} $1"; exit 1; }

# ---------- Defaults ----------------------------------------------------------
THREADS=60
DEPTH=5
RUN_NUCLEI=false
RUN_SHOT=false
SUBJACK_TIMEOUT=30
NUCLEI_TEMPLATES="~/.config/nuclei-templates"

# ---------- getopts -----------------------------------------------------------
usage(){ cat <<EOF
Usage: $0 [-t threads] [--depth N] [--nuclei] [--shot] target.com
EOF
exit 1; }

PARSED=$(getopt -o t: --long depth:,nuclei,shot -- "$@") || usage
eval set -- "$PARSED"
while true; do
  case "$1" in
    -t) THREADS="$2"; shift 2;;
    --depth) DEPTH="$2"; shift 2;;
    --nuclei) RUN_NUCLEI=true; shift;;
    --shot) RUN_SHOT=true; shift;;
    --) shift; break;;
    *) usage;;
  esac
done
[[ $# -ne 1 ]] && usage
TARGET=$1

# ---------- Dependency Check --------------------------------------------------
DEPS=(subfinder amass assetfinder dnsx httpx katana gau nuclei jq subjack)
$RUN_SHOT && DEPS+=(gowitness)
for bin in "${DEPS[@]}"; do command -v $bin >/dev/null 2>&1 || fail "$bin not installed"; done
HAS_GF=$(command -v gf >/dev/null && echo true || echo false)
HAS_GAU=$(command -v gauplus >/dev/null && echo gauplus || echo gau)

# ---------- Setup -------------------------------------------------------------
STAMP=$(date +%Y%m%d-%H%M%S)
OUTDIR="recon-${TARGET}-${STAMP}"
mkdir -p "$OUTDIR"/{subs,katana,nuclei,shots,subjack,logs}
cd "$OUTDIR"
info "Output → $PWD"

# ---------- 1. Passive Subdomain Enumeration ----------------------------------
info "Passive subdomain enumeration…"
subfinder -d "$TARGET" -silent | tee subs/subfinder.txt >/dev/null &
amass enum -passive -d "$TARGET" -silent | tee subs/amass.txt >/dev/null &
assetfinder --subs-only "$TARGET" | tee subs/assetfinder.txt >/dev/null &
wait
cat subs/*.txt | sort -u > subs/all_passive.txt
PASSIVE_TOTAL=$(wc -l < subs/all_passive.txt)
info "Passive total: $PASSIVE_TOTAL"

# ---------- 2. DNS Resolution (dnsx) & HTTPS live check (httpx) ----------------
info "Resolving & probing HTTPS…"
cat subs/all_passive.txt | dnsx -silent -resp-only -rL /etc/resolv.conf | sort -u > subs/resolved.txt
RESOLVED=$(wc -l < subs/resolved.txt)
cat subs/resolved.txt | httpx -silent -nc -tls-probe -status-code -threads "$THREADS" | grep '^https://' | tee live.txt >/dev/null
LIVE=$(wc -l < live.txt)
info "Resolved: $RESOLVED / Live HTTPS: $LIVE"

# ---------- 3. URL fetch (gau/gauplus) ----------------------------------------
info "Fetching archived URLs with $HAS_GAU…"
cat subs/all_passive.txt | $HAS_GAU -silent | sort -u > urls.txt
URLS=$(wc -l < urls.txt)
info "URLs collected: $URLS"

# ---------- 4. Katana Deep Crawl ----------------------------------------------
info "Deep crawling with Katana (depth=$DEPTH)…"
KARGS="-silent -d $DEPTH -c $THREADS -js-crawl -f key -f kv -f qurl"
cat live.txt | cut -d ' ' -f1 | xargs -P "$THREADS" -I{} bash -c 'katana -u "$1" $KARGS -o "katana/$(echo "$1" | sed "s|https*://||;s|/|_|g").txt"' -- {}
find katana -type f -size +0 -exec cat {} + | sort -u > endpoints.txt
ENDP=$(wc -l < endpoints.txt)
info "Endpoints: $ENDP"

# ---------- 5. Secret hunting (gf) --------------------------------------------
if $HAS_GF; then
  info "Running gf patterns for secrets…";
  patterns=(aws-keys apikey firebase key)
  echo "${patterns[@]}" | tr ' ' '\n' > logs/gf-patterns.txt
  cat endpoints.txt | gf "$(IFS=, ; echo "${patterns[*]}")" | sort -u > secrets.txt || true
  [[ -s secrets.txt ]] && info "Potential secrets → secrets.txt ( $(wc -l < secrets.txt) lines )" || info "No secrets found"
else
  warn "gf not installed → skipping secret search"
fi

# ---------- 6. Subjack takeover scan ------------------------------------------
info "Checking for subdomain takeover with subjack…"
cat live.txt | cut -d ' ' -f1 | sed -E 's|https?://([^/]+)/?.*|\1|' | sort -u > subs/livehosts.txt
subjack -w subs/livehosts.txt -t "$THREADS" -timeout "$SUBJACK_TIMEOUT" -ssl -o subjack/takeovers.txt || warn "subjack run encountered issues"
TAK=$( [[ -f subjack/takeovers.txt ]] && wc -l < subjack/takeovers.txt || echo 0 )
[[ $TAK -gt 0 ]] && info "Potential takeovers → subjack/takeovers.txt ( $TAK )" || info "No takeover candidates found"

# ---------- 7. Optional Nuclei Scan -------------------------------------------
if $RUN_NUCLEI; then
  info "Running nuclei (fast templates)…"
  cat live.txt | cut -d ' ' -f1 | nuclei -silent -templates "$NUCLEI_TEMPLATES" -o nuclei/findings.txt
  [[ -s nuclei/findings.txt ]] && info "Nuclei findings saved → nuclei/findings.txt" || info "No nuclei findings"
fi

# ---------- 8. Optional Screenshots -------------------------------------------
if $RUN_SHOT; then
  info "Taking screenshots with gowitness…"
  gowitness file -f live.txt --threads "$THREADS" --timeout 15s --destination shots >/dev/null
  info "Screenshots saved in shots/"
fi

# ---------- 9. Finish ----------------------------------------------------------
cat <<SUMMARY
${C4}\n====================== SUMMARY ======================${C0}
Subdomains (total) : $PASSIVE_TOTAL
Live HTTPS         : $LIVE
Endpoints          : $ENDP
URLs (Archive)     : $URLS
Secrets (gf)       : $( [[ -f secrets.txt ]] && wc -l < secrets.txt || echo 0 )
Takeover candidates: $TAK
Nuclei findings    : $( [[ -f nuclei/findings.txt ]] && wc -l < nuclei/findings.txt || echo 0 )
Screenshots        : $( $RUN_SHOT && ls shots | wc -l || echo 0 )
Output directory   : $PWD
=====================================================
SUMMARY