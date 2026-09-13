import unittest

from config import BuildConfig
from kernel_builder import KernelBuilder


class MemoryFile:
    def __init__(self, content):
        self.content = content

    def read_text(self):
        return self.content

    def write_text(self, content):
        self.content = content


class SusfsStatfsDeclarationTest(unittest.TestCase):
    def test_moves_declaration_before_first_use(self):
        declaration = "extern int susfs_sus_kstat_spoof_vfs_statfs(struct inode *inode, struct kstatfs *buf, bool *is_fuse);"
        helper = "static int susfs_statfs_by_dentry(struct dentry *dentry, struct kstatfs *buf, bool *is_fuse)"
        source = f"#ifdef CONFIG_KSU_SUSFS_SUS_KSTAT\n{helper}\n{{\n\tsusfs_sus_kstat_spoof_vfs_statfs(inode, buf, is_fuse);\n}}\n{declaration}\n#endif\n"
        statfs_file = MemoryFile(source)
        KernelBuilder._fix_susfs_statfs_declaration(statfs_file)
        fixed_source = statfs_file.read_text()
        KernelBuilder._fix_susfs_statfs_declaration(statfs_file)
        self.assertLess(fixed_source.index(declaration), fixed_source.index(helper))
        self.assertEqual(fixed_source.count(declaration), 1)
        self.assertEqual(statfs_file.read_text(), fixed_source)


class SusfsCommitCompatibilityTest(unittest.TestCase):
    def test_android13_5_10_uses_sukisu_4_2_compatible_susfs_commit(self):
        config = BuildConfig(android_version="android13", kernel_version="5.10", sub_level="198", os_patch_level="2024-06")
        self.assertEqual(config.resolved_susfs_commit, "818714ed0c7f13f478b0d80541c76abb9e71d3c6")

    def test_explicit_susfs_commit_takes_precedence(self):
        config = BuildConfig(android_version="android13", kernel_version="5.10", sub_level="198", os_patch_level="2024-06", susfs_commit="abcdef1")
        self.assertEqual(config.resolved_susfs_commit, "abcdef1")


if __name__ == "__main__":
    unittest.main()
