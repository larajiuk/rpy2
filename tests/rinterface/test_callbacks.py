from . import utils
import pytest
import sys
import tempfile
import rpy2.rinterface as rinterface

rinterface.initr()

def is_AQUA_or_Windows():
    platform = rinterface.baseenv.get('.Platform')
    _ = platform.do_slot('names')
    platform_gui = _[_.index('GUI')]
    platform_ostype = _[_.index('OS.type')]
    if (platform_gui == 'AQUA') or (platform_ostype == 'windows'):
        return True
    else:
        return False


def test_set_consolewrite_print():
    buf = []
    def f(x):
        buf.append(x)

    with utils.obj_in_module(rinterface.callbacks, 'consolewrite_print', f):
        code = rinterface.StrSexpVector(["3", ])
        rinterface.baseenv["print"](code)
        assert '[1] "3"\n' == str.join('', buf)


def test_consolewrite_print_error():

    exceptions = []
    def f(x):
        try:
            raise Exception("Doesn't work.")
        except Exception as e:
            exceptions.append(str(e))

    with utils.obj_in_module(rinterface.callbacks, 'consolewrite_print', f):
        code = rinterface.StrSexpVector(["3", ])
        rinterface.baseenv["print"](code)
        assert "Doesn't work." == exceptions[0]


def testSetResetConsole():
    reset = [0]
    def f():
        reset[0] += 1

    with utils.obj_in_module(rinterface.callbacks, 'consolereset', f):
        with pytest.raises(rinterface._rinterface.RRuntimeError), \
             pytest.warns(rinterface.RRuntimeWarning):
                rinterface.baseenv['eval'](rinterface.parse('1+"a"'))
        assert reset[0] == 1

    
@pytest.mark.skip(is_AQUA_or_Windows(),
                  reason='Can only be tested on Aqua or Windows')
def test_set_flushconsole():
    flush = {'count': 0}
    def f():
        flush['count'] = flush['count'] + 1

    with utils.obj_in_module(rinterface.callbacks, 'consoleflush', f):
        assert rinterface.get_flushconsole() == f
        rinterface.baseenv.get('flush.console')()
        assert flush['count'] == 1
        rinterface.set_writeconsole_regular(rinterface.consoleFlush)


@pytest.mark.skip(is_AQUA_or_Windows(),
                  reason='Can only be tested on Aqua or Windows')
def test_flushconsole_with_error():
    def f(prompt):
        raise Exception("Doesn't work.")

    with utils.obj_in_module(rinterface.callbacks, 'consoleflush', f):
        with pytest.raises(Exception):
            res = rinterface.baseenv.get('flush.console')()


def test_consoleread():
    yes = 'yes\n'
    def sayyes(prompt):
        return yes
    with utils.obj_in_module(rinterface.callbacks, 'consoleread', sayyes):
        res = rinterface.baseenv['readline']()
        assert yes.strip() == res[0]


def test_console_read_with_error():
    def f(prompt):
        raise Exception("Doesn't work.")
    with utils.obj_in_module(rinterface.callbacks, 'consoleread', f):
        with pytest.raises(Exception):
            res = rinterface.baseenv['readline']()


def test_show_message():
    def f(message):
        return 'foo'
    with utils.obj_in_module(rinterface.callbacks, 'showmessage', f):
        pass
    # TODO: incomplete test


def test_show_message_with_error():
    def f(prompt):
        raise Exception("Doesn't work.")
    with utils.obj_in_module(rinterface.callbacks, 'showmessage', f):
        pass
    # TODO: incomplete test


def test_choosefile():
    me = "me"
    def chooseMe(new):
        return me
    with utils.obj_in_module(rinterface.callbacks, 'choosefile', chooseMe):
        res = rinterface.baseenv['file.choose']()
        assert me == res[0]


def test_choosefile_error():
    def f(prompt):
        raise Exception("Doesn't work.")

    with utils.obj_in_module(rinterface.callbacks,
                             'consolewrite_print',
                             utils.noconsole):
        with utils.obj_in_module(rinterface.callbacks, 'choosefile', f):
            with pytest.raises(rinterface._rinterface.RRuntimeError):
                with pytest.warns(rinterface.RRuntimeWarning):
                    rinterface.baseenv["file.choose"]()


@pytest.mark.skip(reason='WIP')    
def test_showfiles():
    sf = []
    def f(fileheaders, wtitle, fdel, pager):
        sf.append(wtitle)
        for tf in fileheaders:
            sf.append(tf)

    with utils.obj_in_module(rinterface.callbacks, 'showfiles', f):
        file_path = rinterface.baseenv['file.path']
        r_home = rinterface.baseenv['R.home']
        filename = file_path(r_home(rinterface.StrSexpVector(('doc', ))), 
                             rinterface.StrSexpVector(('COPYRIGHTS', )))
        res = rinterface.baseenv['file.show'](filename)
        assert filename[0] == sf[1][1]
        assert 'R Information' == sf[0]


@pytest.mark.skip(reason='WIP')    
def test_showfiles_error():
    def f(fileheaders, wtitle, fdel, pager):
        raise Exception("Doesn't work.")

    with utils.obj_in_module(rinterface.callbacks, 'showfiles', f):
        file_path = rinterface.baseenv['file.path']
        r_home = rinterface.baseenv['R.home']
        filename = file_path(r_home(rinterface.StrSexpVector(('doc', ))), 
                             rinterface.StrSexpVector(('COPYRIGHTS', )))
        with pytest.raises(Exception):
            rinterface.baseenv['file.show'](filename)


@pytest.mark.skip(reason='WIP')
def test_cleanup():
    def f(saveact, status, runlast):
        return None
    with utils.obj_in_module(rinterface.callbacks, 'cleanup', f):
        r_quit = rinterface.baseenv['q']
        with pytest.raises(rinterface._rinterface.RRuntimeError):
            r_quit()
