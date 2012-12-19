# -*- coding: utf-8 -*-
#   Copyright 2012 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2012 Red Hat, Inc.
#
#   This is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.

from sm import main
from sm.parser import parse_string

SCRIPT = '''
sm arg_of_fn_call {
  stateful decl any_pointer arg0;
  decl any_expr arg1;
  decl any_expr arg2;

  arg0.all:
    { test2(arg0, arg1, arg2) } => {{ error('test2() was called with arg0:%s arg1:%s arg2:%s' % (arg0, arg1, arg2)) }};
}
'''

checker = parse_string(SCRIPT)
main([checker])
