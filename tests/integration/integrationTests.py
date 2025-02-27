import subprocess

def test1():
    res = subprocess.run(["build/app.exe"], input="(2+3)+(1+4)*(1-3)",text=True,capture_output=True)
    assert res.returncode == 0
    assert int(res.stdout) == -5


def test2():
    res = subprocess.run(["build/app.exe"], input="(100 - (25 + 15) / 5) * (3 + 7) - 48 / 6",text=True,capture_output=True)
    assert res.returncode == 0
    assert int(res.stdout) == 912


def test3():
    res = subprocess.run(["build/app.exe", "--float"], input="((36/6+4)*(10-3*2)+12)/(5+1)",text=True,capture_output=True)
    assert res.returncode == 0
    assert float(res.stdout) == 8.6667


def test4():
    res = subprocess.run(["build/app.exe"], input="((120 / (10 + 2) + (7 * 4 - 5)) * (3 + 2) - 18)",text=True,capture_output=True)
    assert res.returncode == 0
    assert int(res.stdout) == 147


def test5():
    res = subprocess.run(["build/app.exe", "--float"], input="((16+24)/(8-3)*(5+2))+(12*3-10)/7",text=True,capture_output=True)
    assert res.returncode == 0
    assert float(res.stdout) == 59.7143


def test6():
    res=subprocess.run(["build/app.exe", "--float"], input="((((415-323) * 2314 /322) + (44-77) / 13) - (552 - 21 * 43))",text=True,capture_output=True)
    assert res.returncode == 0
    assert float(res.stdout) == 1009.6044


def test7():
    res=subprocess.run(["build/app.exe"], input="((5+15)*(20/4-2)+8)*(3-1)",text=True,capture_output=True)
    assert res.returncode == 0
    assert int(res.stdout) == 136


#error tests
def test8():
    res=subprocess.run(["build/app.exe"], input="10/(2-2)", text=True, capture_output=True)
    assert res.returncode != 0


def test9():
    res=subprocess.run(["build/app.exe", "--float"], input="-10 + 5",text=True,capture_output=True)
    assert res.returncode != 0


def test10():
    res=subprocess.run(["build/app.exe"], input="10/(2-2)", text=True, capture_output=True)
    assert res.returncode != 0


def test11():
    res=subprocess.run(["build/app.exe", "--float"], input="1 +- 2",text=True,capture_output=True)
    assert res.returncode != 0


def test12():
    res=subprocess.run(["build/app.exe"], input="1 2 3 4", text=True, capture_output=True)
    assert res.returncode != 0


def test13():
    res=subprocess.run(["build/app.exe"], input="1 + 2 /", text=True, capture_output=True)
    assert res.returncode != 0