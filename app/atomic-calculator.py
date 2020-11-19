import PySimpleGUI as _sg

_functions = {}


def _register(fun):
    _functions[fun.__name__] = fun
    return fun


@_register
def cg(j1, m1, j2, m2, j3, m3):
    """
    cg(j1,m1,j2,m2,j3,m3)
        计算CG系数: C^{j3m3}_{j1m1,j2m2}
    """
    from sympy.physics.quantum import cg
    from sympy import S
    from fractions import Fraction
    def _mapfun(arg):
        arg = Fraction(arg)
        arg = S(arg.numerator) / S(arg.denominator)
        return arg

    j1, m1, j2, m2, j3, m3 = map(_mapfun, (j1, m1, j2, m2, j3, m3))
    c = cg.CG(j1, m1, j2, m2, j3, m3)
    return c.simplify()


@_register
def wigner3j(j1, j2, j3, m1, m2, m3):
    """
    wigner3j(j1,j2,j3,m1,m2,m3)
        计算Wigner3j系数[j1,j2,j3;m1,m2,m3]
    """
    from sympy.physics.quantum import cg
    from sympy import S
    from fractions import Fraction
    def _mapfun(arg):
        arg = Fraction(arg)
        arg = S(arg.numerator) / S(arg.denominator)
        return arg

    j1, j2, j3, m1, m2, m3 = map(_mapfun, (j1, j2, j3, m1, m2, m3))
    c = cg.wigner_3j(j1, j2, j3, m1, m2, m3)
    try:
        return c.simplify()
    except AttributeError:
        return c


@_register
def wigner6j(j1, j2, j3, j4, j5, j6):
    """
    wigner6j(j1,j2,j3,j4,j5,j6)
        计算Wigner6j系数[j1,j2,j3;j4,j5,j6]
    """
    from sympy.physics.quantum import cg
    from sympy import S
    from fractions import Fraction
    def _mapfun(arg):
        arg = Fraction(arg)
        arg = S(arg.numerator) / S(arg.denominator)
        return arg

    j1, j2, j3, j4, j5, j6 = map(_mapfun, (j1, j2, j3, j4, j5, j6))
    c = cg.wigner_6j(j1, j2, j3, j4, j5, j6)
    try:
        return c.simplify()
    except AttributeError:
        return c


def _parse_function(fun):
    import inspect
    sig = inspect.signature(fun)
    argcount = len(sig.parameters)
    argnames = str(sig).strip()[1:-1].split(',')
    return argcount, argnames


_help_text = """
version: 0.1


公式：
    {}


键盘绑定：

    CTRL + F    -       一键清除输入文本
    ENTER       -       显示输出结果
    ESC         -       关闭窗口
    F1          -       查看帮助

""".format("".join('%s' % (_f.__doc__) for _f in _functions.values()), )

_history = []
_p = -1


def _validate(text):
    for s in text.split():
        if s.strip().startswith('_'):
            return False
        if s in ('eval', 'exec'):
            return False
    for s in ['=', 'import', 'from', ';']:
        if s in text:
            return False
    return True


_menu_def = [['&Help', '&About']]
# All the stuff inside your window.
_main_layout = [[_sg.Menu(_menu_def)],
                [_sg.Text('可选函数:'),
                 _sg.Listbox(values=list(_functions.keys()), size=(12, 7), key='-LIST-', enable_events=True),
                 _sg.Multiline(tooltip='function info', disabled=True, key='-INFO-', size=(25, 7))],
                [_sg.Text('输入:'), _sg.InputText(key='-IN-')],
                [_sg.Text('结果:'), _sg.Text('', size=(40, 1), key='-OUTPUT-')],
                [_sg.Multiline(tooltip='history', disabled=True, key='-HISTORY-'), _sg.Button('Save')],
                [_sg.Button('Calculate', bind_return_key=True), _sg.Button('Exit')]]

# Create the Window
_window = _sg.Window('常用科学计算器', _main_layout, return_keyboard_events=True)

# Event Loop to process "events" and get the "values" of the inputs
while True:
    _event, _values = _window.read()
    # print(_event)
    if _event == 'Up:38':
        try:
            if _p - 1 < 0:
                continue
            _window['-IN-'].Update(_history[_p - 1])
        except IndexError:
            pass
        else:
            _p -= 1
    if _event == 'Down:40':
        try:
            _window['-IN-'].Update(_history[_p + 1])
        except IndexError:
            pass
        else:
            _p += 1
    if _event in (None, 'Exit', 'Escape:27'):  # if user closes window or clicks cancel
        break
    if _event in ('About', 'F1:112'):
        _sg.Popup(_help_text, title='帮助文件')
    if _event == 'Save':
        _save_layout = [[_sg.Text('Filename')],
                        [_sg.Input(), _sg.FileBrowse(file_types=(("Text Files", "*.txt"),))],
                        [_sg.OK(), _sg.Cancel()]]
        _save_window = _sg.Window('Save History', _save_layout)
        _event, _values = _save_window.read()
        _save_window.close()
        if _event == 'OK':
            _filename = _values[0]
            try:
                with open(_filename, 'w', encoding='utf-8') as _fp:
                    _fp.write(_window['-HISTORY-'].Get())
                _sg.popup('save history to', _filename)
            except:
                continue
    if _event == 'Calculate':
        _inp = _values['-IN-']
        try:
            if not _validate(_inp):
                raise SyntaxError('invalid input')
            _res = str(eval(_inp))
        except Exception as _e:
            _res = str(_e)
        _window['-OUTPUT-'].Update(_res)
        _window['-HISTORY-'].Update(_inp + '  -->  ' + _res + '\n', append=True, autoscroll=True)
        _history.append(_inp)
        _p = len(_history) - 1
    if _event in ('Control_L:17', 'Control_R:17'):
        _event, _ = _window.read(timeout=500)
        if _event in ('f', 'F'):
            _window['-IN-'].Update('')
            _window['-OUTPUT-'].Update('')
    if _event == '-LIST-':
        _funname = _values['-LIST-'][0]
        _fun = _functions[_funname]
        _argcount, _argnames = _parse_function(_fun)
        _window['-INFO-'].Update(
            'argcount: %s, argnames: %s\ninfo: %s' % (_argcount, ','.join(_argnames), _fun.__doc__))
        _window['-IN-'].Update('%s(%s)' % (_funname, ',' * (_argcount - 1)))

_window.close()
