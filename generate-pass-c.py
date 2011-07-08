#   Copyright 2011 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2011 Red Hat, Inc.
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

from cpybuilder import *

cu = CompilationUnit()
cu.add_include('gcc-python.h')
cu.add_include('gcc-python-wrappers.h')
cu.add_include('gcc-plugin.h')
cu.add_include("tree-pass.h")

modinit_preinit = ''
modinit_postinit = ''

# See GCC's tree-pass.h

def generate_pass():
    global modinit_preinit
    global modinit_postinit

    getsettable = PyGetSetDefTable('gcc_Pass_getset_table', [],
                                   identifier_prefix='gcc_Pass',
                                   typename='PyGccPass')
    getsettable.add_simple_getter(cu,
                                  'name',
                                  'gcc_python_string_from_string(self->pass->name)',
                                  'Name of the pass')
    getsettable.add_simple_getter(cu,
                                  'next',
                                  'gcc_python_make_wrapper_pass(self->pass->next)',
                                  'The next gcc.Pass after this one, or None')
    getsettable.add_simple_getter(cu,
                                  'sub',
                                  'gcc_python_make_wrapper_pass(self->pass->sub)',
                                  "The first sub-pass (gated by this pass' predicate, if any)")

    for field in ('properties_required', 'properties_provided', 'properties_destroyed'):
        getsettable.add_simple_getter(cu,
                                      field,
                                      'gcc_python_int_from_long(self->pass->%s)' % field,
                                      None)
    cu.add_defn(getsettable.c_defn())

    methods = PyMethodTable('gcc_Pass_methods', [])
    methods.add_method('get_roots',
                       'gcc_Pass_get_roots',
                       'METH_CLASS | METH_VARARGS',
                       "Get a tuple of gcc.Pass instances, the roots of the compilation pass tree")
    cu.add_defn(methods.c_defn())
    
    pytype = PyTypeObject(identifier = 'gcc_PassType',
                          localname = 'Pass',
                          tp_name = 'gcc.Pass',
                          struct_name = 'struct PyGccPass',
                          tp_new = 'PyType_GenericNew',
                          tp_getset = getsettable.identifier,
                          tp_repr = '(reprfunc)gcc_Pass_repr',
                          tp_str = '(reprfunc)gcc_Pass_repr',
                          tp_methods = methods.identifier,
                          )
    cu.add_defn(pytype.c_defn())
    modinit_preinit += pytype.c_invoke_type_ready()
    modinit_postinit += pytype.c_invoke_add_to_module()

generate_pass()

def generate_pass_subclasses():
    global modinit_preinit
    global modinit_postinit

    for opt_pass_type in ('GIMPLE_PASS', 'RTL_PASS',
                          'SIMPLE_IPA_PASS', 'IPA_PASS'):
        cc = camel_case(opt_pass_type)
        pytype = PyTypeObject(identifier = 'gcc_%sType' % cc,
                              localname = cc,
                              tp_name = 'gcc.%s' % cc,
                              struct_name = 'struct PyGccPass',
                              tp_new = 'PyType_GenericNew',
                              tp_base = '&gcc_PassType',
                              )
        cu.add_defn(pytype.c_defn())
        modinit_preinit += pytype.c_invoke_type_ready()
        modinit_postinit += pytype.c_invoke_add_to_module()

generate_pass_subclasses()

cu.add_defn("""
int autogenerated_pass_init_types(void)
{
""" + modinit_preinit + """
    return 1;

error:
    return 0;
}
""")

cu.add_defn("""
void autogenerated_pass_add_types(PyObject *m)
{
""" + modinit_postinit + """
}
""")

print(cu.as_str())
