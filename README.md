# Inzetbooster

## Installation

### uv

If you use [uv](https://github.com/astral-sh/uv) installation is done using the
standard `venv` and `sync` commands:

```text
uv venv
uv pip sync requirements.txt
uv pip install -e .
```

<details>
<summary>Details</summary>

```shell
$ uv venv
Using Python 3.12.2 interpreter at: /opt/homebrew/opt/python@3.12/bin/python3.12
Creating virtualenv at: .venv
Activate with: source .venv/bin/activate

$ uv pip sync requirements.txt
Installed 12 packages in 7ms
 + anyio==4.3.0
 + beautifulsoup4==4.12.3
 + certifi==2024.2.2
 + h11==0.14.0
 + html5lib==1.1
 + httpcore==1.0.4
 + httpx==0.27.0
 + idna==3.6
 + six==1.16.0
 + sniffio==1.3.1
 + soupsieve==2.5
 + webencodings==0.5.1

✦ ❯ uv pip install -e .
   Built file:///home/wichert/hack/inzetbooster
Built 1 editable in 364ms
Resolved 13 packages in 1ms
Installed 1 package in 0ms
 + inzetbooster==1.0.0 (from file:///home/wichert/hack/inzetbooster)
```

</details>

You can now run the generated `inzetbooster` command:

```shell
$ .venv/bin/inzetbooster --org=myorg export-shifts
"Dienst_id","Groep_id","Groep_naam","Datum","Dag","Starttijd","Eindtijd","Tijdsduur","Gebruiker_id","Naam","Email","Telefoon","Locatie_id","Locatie_naam","Afwezig","Geannuleerd","Starred","Opmerkingen"
```

### venv

It is strongly recommended to use a [virtual environment](https://docs.python.org/3/library/venv.html) to install inzetbooster.

```text
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
```

<details>
<summary>Details</summary>

```shell
$ python3 -m venv .venv

$ .venv/bin/pip install -r requirements.txt
Collecting anyio==4.3.0 (from -r requirements.txt (line 3))
  Downloading anyio-4.3.0-py3-none-any.whl (85 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 85.6/85.6 kB 1.3 MB/s eta 0:00:00
.
.
.

Installing collected packages: webencodings, soupsieve, sniffio, six, idna, h11, certifi, httpcore, html5lib, beautifulsoup4, anyio, httpx
Successfully installed anyio-4.3.0 beautifulsoup4-4.12.3 certifi-2024.2.2 h11-0.14.0 html5lib-1.1 httpcore-1.0.4 httpx-0.27.0 idna-3.6 six-1.16.0 sniffio-1.3.1 soupsieve-2.5 webencodings-0.5.1

$ .venv/bin/pip install -e .
Obtaining file:///home/wichert/hack/inzetbooster
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Requirement already satisfied: beautifulsoup4 in ./.venv/lib/python3.12/site-packages (from inzetbooster==1.0.0) (4.12.3)
Requirement already satisfied: html5lib in ./.venv/lib/python3.12/site-packages (from inzetbooster==1.0.0) (1.1)
Requirement already satisfied: httpx in ./.venv/lib/python3.12/site-packages (from inzetbooster==1.0.0) (0.27.0)
Requirement already satisfied: soupsieve>1.2 in ./.venv/lib/python3.12/site-packages (from beautifulsoup4->inzetbooster==1.0.0) (2.5)
Requirement already satisfied: six>=1.9 in ./.venv/lib/python3.12/site-packages (from html5lib->inzetbooster==1.0.0) (1.16.0)
Requirement already satisfied: webencodings in ./.venv/lib/python3.12/site-packages (from html5lib->inzetbooster==1.0.0) (0.5.1)
Requirement already satisfied: anyio in ./.venv/lib/python3.12/site-packages (from httpx->inzetbooster==1.0.0) (4.3.0)
Requirement already satisfied: certifi in ./.venv/lib/python3.12/site-packages (from httpx->inzetbooster==1.0.0) (2024.2.2)
Requirement already satisfied: httpcore==1.* in ./.venv/lib/python3.12/site-packages (from httpx->inzetbooster==1.0.0) (1.0.4)
Requirement already satisfied: idna in ./.venv/lib/python3.12/site-packages (from httpx->inzetbooster==1.0.0) (3.6)
Requirement already satisfied: sniffio in ./.venv/lib/python3.12/site-packages (from httpx->inzetbooster==1.0.0) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in ./.venv/lib/python3.12/site-packages (from httpcore==1.*->httpx->inzetbooster==1.0.0) (0.14.0)
Building wheels for collected packages: inzetbooster
  Building editable for inzetbooster (pyproject.toml) ... done
  Created wheel for inzetbooster: filename=inzetbooster-1.0.0-py3-none-any.whl size=1913 sha256=b163cff437aa45bb58bea3522f2dbc59d709144cf044fd089c3a52f442262352
  Stored in directory: /private/var/folders/x7/p22c5nfj3wvgj4fv7qxnz1bw0000gn/T/pip-ephem-wheel-cache-n6iw2_a0/wheels/92/12/a1/5cd52186aa4b5f58c6980b4585c864c677b9424b842308daa6
Successfully built inzetbooster
Installing collected packages: inzetbooster
Successfully installed inzetbooster-1.0.0
```

</details>

You can now run the generated `inzetbooster` command:

```shell
$ .venv/bin/inzetbooster --org=myorg export-shifts
"Dienst_id","Groep_id","Groep_naam","Datum","Dag","Starttijd","Eindtijd","Tijdsduur","Gebruiker_id","Naam","Email","Telefoon","Locatie_id","Locatie_naam","Afwezig","Geannuleerd","Starred","Opmerkingen"
```

## Update requirements.txt

`uv` is used to update the requirements file:

```shell
$ uv pip compile pyproject.toml -o requirements.txt --generate-hashes --all-extras > requirements.txt
warning: Requirements file requirements.txt does not contain any dependencies
Resolved 12 packages in 427ms
```
