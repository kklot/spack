# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class EcpDataVisSdk(BundlePackage, CudaPackage):
    """ECP Data & Vis SDK"""

    homepage = "https://github.com/chuckatkins/ecp-data-viz-sdk"

    tags = ['ecp']
    maintainers = ['chuckatkins']

    version('1.0')

    ############################################################
    # Variants
    ############################################################

    # I/O
    variant('adios2', default=False, description="Enable ADIOS2")
    variant('darshan', default=False, description="Enable Darshan")
    variant('faodel', default=False, description="Enable FAODEL")
    variant('hdf5', default=False, description="Enable HDF5")
    variant('pnetcdf', default=False, description="Enable PNetCDF")
    variant('unifyfs', default=False, description="Enable UnifyFS")
    variant('veloc', default=False, description="Enable VeloC")

    # Vis
    variant('ascent', default=False, description="Enable Ascent")
    variant('paraview', default=False, description="Enable ParaView")
    variant('sz', default=False, description="Enable SZ")
    variant('vtkm', default=False, description="Enable VTK-m")
    variant('zfp', default=False, description="Enable ZFP")

    # Cinema
    variant('cinema', default=False, description="Enable Cinema")

    # Outstanding build issues
    variant('sensei', default=False, description="Enable Sensei")
    conflicts('+sensei')
    variant('visit', default=False, description="Enable VisIt")
    conflicts('+visit')

    # Wrapper around depends_on to propagate dependency variants
    def dav_sdk_depends_on(spec, when=None, propagate=None):
        # Do the basic depends_on
        depends_on(spec, when=when)

        # Strip spec string to just the base spec name
        # ie. A +c ~b -> A
        spec = Spec(spec).name

        if '+' in when and len(when.split()) == 1:
            when_not = when.replace('+', '~')
            # If the package is in the spec tree then it must
            # be enabled in the SDK.
            conflicts(when_not, '^' + spec)

        # Skip if there is nothing to propagate
        if not propagate:
            return

        # Map the propagated variants to the dependency variant
        if not type(propagate) is dict:
            propagate = dict([(v, v) for v in propagate])

        # Determine the base variant
        base_variant = ''
        if when:
            base_variant = when

        def is_boolean(variant):
            return '=' not in variant

        # Propagate variants to dependecy
        for v_when, v_then in propagate.items():
            if is_boolean(v_when):
                depends_on('{0} +{1}'.format(spec, v_then),
                           when='{0} +{1}'.format(base_variant, v_when))
                depends_on('{0} ~{1}'.format(spec, v_then),
                           when='{0} ~{1}'.format(base_variant, v_when))
            else:
                depends_on('{0} {1}'.format(spec, v_then),
                           when='{0} {1}'.format(base_variant, v_when))

    def exclude_variants(variants, exclude):
        return [variant for variant in variants if variant not in exclude]

    ############################################################
    # Dependencies
    ############################################################
    cuda_arch_variants = ['cuda_arch={0}'.format(x)
                          for x in CudaPackage.cuda_arch_values]

    dav_sdk_depends_on('adios2+shared+mpi+fortran+python+blosc+sst+ssc+dataman',
                       when='+adios2',
                       propagate=['hdf5', 'sz', 'zfp'])

    dav_sdk_depends_on('darshan-runtime+mpi', when='+darshan')
    dav_sdk_depends_on('darshan-util', when='+darshan')

    dav_sdk_depends_on('faodel+shared+mpi network=libfabric',
                       when='+faodel',
                       propagate=['hdf5'])

    dav_sdk_depends_on('hdf5@1.12: +shared+mpi+fortran', when='+hdf5')

    dav_sdk_depends_on('parallel-netcdf+shared+fortran', when='+pnetcdf')

    dav_sdk_depends_on('unifyfs', when='+unifyfs ')

    dav_sdk_depends_on('veloc', when='+veloc')

    # Currenly only develop has necessary patches. Update this after SC21 release
    propagate_to_sensei = [(v, v) for v in ['adios2', 'ascent', 'hdf5', 'vtkm']]
    propagate_to_sensei.extend([('paraview', 'catalyst'), ('visit', 'libsim')])
    dav_sdk_depends_on('sensei@develop +vtkio +python ~miniapps', when='+sensei',
                       propagate=dict(propagate_to_sensei))

    # Need to explicitly turn off conduit hdf5_compat in order to build
    # hdf5@1.12 which is required for SDK
    dav_sdk_depends_on('ascent+shared+mpi+fortran+openmp+python+vtkh+dray',
                       when='+ascent')
    depends_on('ascent ^conduit ~hdf5_compat', when='+ascent +hdf5')

    depends_on('py-cinemasci', when='+cinema')

    dav_sdk_depends_on('paraview +mpi +python3 +kits',
                       when='+paraview',
                       propagate=['hdf5', 'adios2'] + cuda_arch_variants)
    # Want +shared when not using cuda
    depends_on('paraview ~shared +cuda', when='+paraview +cuda')
    depends_on('paraview +shared ~cuda', when='+paraview ~cuda')

    dav_sdk_depends_on('visit', when='+visit')

    dav_sdk_depends_on('vtk-m+shared+mpi+openmp+rendering',
                       when='+vtkm',
                       propagate=['cuda'] + cuda_arch_variants)

    # +python is currently broken in sz
    # dav_sdk_depends_on('sz+shared+fortran+python+random_access',
    dav_sdk_depends_on('sz+shared+fortran+random_access',
                       when='+sz',
                       propagate=['hdf5'])

    dav_sdk_depends_on('zfp',
                       when='+zfp',
                       propagate=['cuda'] + cuda_arch_variants)
