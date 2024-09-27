
from main import DLL, Node, Git
from typing import TypeVar, List
import copy
import unittest

# for more information on typehinting, check out https://docs.python.org/3/library/typing.html
T = TypeVar("T")  # represents generic type


class DLLTests(unittest.TestCase):

    def check_dll(self, expected: List[T], dll: DLL, multilevel: bool = False):
        """
        Assert structure of dll is proper and contains the values of result.
        Used as helper function throughout testcases. Not an actual testcase itself.
        Collapse/hide this by clicking the minus arrow on the left sidebar.

        :param expected: list of expected values in dll
        :param dll: DLL to be validated
        :param multilevel: remove the size check for multilevel DLLs
        :return: None. Raises exception and fails testcase if structure is DLL is not properly structured
                 or contains values different from those in result.
        """
        # check size
        if not multilevel:
            self.assertEqual(len(expected), dll.size)

        # short-circuit if empty list
        if len(expected) == 0:
            self.assertIsNone(dll.head)
            self.assertIsNone(dll.tail)
            return

        # check head and tail
        self.assertIsNone(dll.head.prev)
        self.assertIsNone(dll.tail.next)
        if isinstance(expected[0], tuple):
            for j, element in enumerate(expected[0]):
                self.assertEqual(element, dll.head.value[j])
            for j, element in enumerate(expected[-1]):
                self.assertEqual(element, dll.tail.value[j])
        else:
            self.assertEqual(expected[0], dll.head.value)
            self.assertEqual(expected[-1], dll.tail.value)

        # check all intermediate connections and values
        left, right = dll.head, dll.head.next
        i = 0
        while right is not None:
            self.assertIs(left.next, right)
            self.assertIs(left, right.prev)
            if isinstance(expected[i], tuple):
                for j, element in enumerate(expected[i]):
                    self.assertEqual(element, left.value[j])
                for j, element in enumerate(expected[i + 1]):
                    self.assertEqual(element, right.value[j])
            else:
                self.assertEqual(expected[i], left.value)
                self.assertEqual(expected[i + 1], right.value)
            # child node should be None
            self.assertIsNone(right.children_branch)

            left, right = left.next, right.next
            i += 1

        # child node should be None
        self.assertIsNone(left.children_branch)

        # check size after iteration with manual count
        self.assertEqual(len(expected), i + 1, "Number of expected elements and length of DLL do not match")

    def test_empty(self):

        # (1) empty DLL
        dll = DLL()
        self.assertTrue(dll.empty())

        # (2) DLL with one node
        dll.head = dll.tail = Node(1)
        dll.size += 1
        self.assertFalse(dll.empty())

        # (3) DLL with multiple nodes
        for i in range(0, 50):
            dll.tail.next = Node(i, None, dll.tail)
            dll.tail = dll.tail.next
            dll.size += 1
            self.assertFalse(dll.empty())

        # (4) DLL after removing all nodes
        dll.head = dll.tail = None
        dll.size = 0
        self.assertTrue(dll.empty())

    def test_push(self):

        # (1) push single node on back
        dll = DLL()
        dll.push(0)
        self.assertIs(dll.head, dll.tail)  # see note 8 in specs for `is` vs `==`
        self.check_dll([0], dll)  # if failure here, see (1).
        # pro tip: use CTRL + B with your cursor on check_dll to jump to its definition at the top of the file.
        # then, use CTRL + Alt + RightArrow to jump back here!
        # https://www.jetbrains.com/help/pycharm/navigating-through-the-source-code.html

        # (2) push single node on front
        dll = DLL()
        dll.push(0, back=False)
        self.assertIs(dll.head, dll.tail)
        self.check_dll([0], dll)  # if failure here, see (2)

        # (3) push multiple nodes on back
        dll = DLL()
        lst = []
        for i in range(5):
            dll.push(i)
            lst.append(i)
            self.check_dll(lst, dll)  # if failure here, see (3)

        # (4) push multiple nodes on front
        dll = DLL()
        lst = []
        for i in range(5):
            dll.push(i, back=False)
            lst.insert(0, i)
            self.check_dll(lst, dll)  # if failure here, see (4)

        # (5) alternate pushing onto front and back
        dll = DLL()
        lst = []
        for i in range(50):
            dll.push(i, i % 2 == 0)  # push back if i is even, else push front
            if i % 2 == 0:  # pushed back, new tail
                lst.append(i)
                self.check_dll(lst, dll)  # if failure here, see (5)
            else:  # pushed front, new head
                lst.insert(0, i)
                self.check_dll(lst, dll)  # if failure here, see (5)

    def test_pop(self):

        # (1) pop back on empty list (should do nothing)
        dll = DLL()
        try:
            dll.pop()
        except Exception as e:
            self.fail(msg=f"Raised {type(e)} when popping from back of empty list.")

        # (2) pop front on empty list (should do nothing)
        dll = DLL()
        try:
            dll.pop(back=False)
        except Exception as e:
            self.fail(msg=f"Raised {type(e)} when popping from front of empty list.")

        # (3) pop back on multiple node list
        dll = DLL()
        lst = []
        for i in range(5):  # construct list
            dll.push(i)
            lst.append(i)
        for i in range(5):  # destruct list
            dll.pop()
            lst.pop()
            self.check_dll(lst, dll)  # if failure here, see (3)

        # (4) pop front on multiple node list
        dll = DLL()
        lst = []
        for i in range(5):  # construct list
            dll.push(i)
            lst.append(i)
        for i in range(5):  # destruct list
            dll.pop(back=False)
            lst.pop(0)
            self.check_dll(lst, dll)  # if failure here, see (4)

        # (5) alternate popping from front, back
        dll = DLL()
        lst = []
        for i in range(50):
            dll.push(i)
            lst.append(i)
        for end in range(49):  # remove all but one node
            dll.pop(end % 2 == 0)  # pop back if even, front if odd
            if end % 2 == 0:  # removed tail
                lst.pop()
                self.check_dll(lst, dll)  # if failure here, see (5)
            else:  # removed head
                lst.pop(0)
                self.check_dll(lst, dll)  # if failure here, see (5)

        # (6) check there is exactly one node left in DLL (middle of original), then remove
        self.check_dll([24], dll)  # if failure here, see (6)
        dll_copy = copy.deepcopy(dll)
        dll.pop()  # remove tail
        dll_copy.pop(back=False)  # remove head
        self.check_dll([], dll)  # if failure here, see (6)
        self.check_dll([], dll_copy)  # if failure here, see (6)

    def test_list_to_dll(self):

        # (1) create DLL from empty list
        dll = DLL()
        dll.list_to_dll([])
        self.check_dll([], dll)  # if failure here, see (1)

        # (2) create DLL from longer lists
        for i in range(50):
            source = list(range(i))
            dll = DLL()
            dll.list_to_dll(source)
            self.check_dll(source, dll)  # if failure here, see (2)

        # (3) check DLL is cleared and size is reset for each call to list_to_dll
        source = [1, 2, 3, 4]
        dll = DLL()
        dll.list_to_dll(source)
        self.check_dll(source, dll)  # if failure here, see (3) 

        source = [5, 6, 7, 8]
        dll.list_to_dll(source)
        self.check_dll(source, dll)  # if failure here, see (3)

    def test_dll_to_list(self):

        # (1) create list from empty DLL
        dll = DLL()
        output = dll.dll_to_list()
        self.check_dll(output, dll)  # if failure here, see (1)

        # (2) create list from longer DLLs
        for i in range(50):
            dll = DLL()
            for j in range(i):
                dll.push(j)
            output = dll.dll_to_list()
            self.check_dll(output, dll)  # if failure here, see (2)

    def test_find(self):

        # (1) find in empty DLL
        dll = DLL()
        node = dll.find(331)
        self.assertIsNone(node)

        # (2) find existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        node = dll.find(0)
        self.assertIsInstance(node, Node)
        self.assertEqual(0, node.value)
        self.assertIsNone(node.next)
        self.assertIsNone(node.prev)

        # (3) find non-existing value in single-node DLL
        node = dll.find(331)
        self.assertIsNone(node)

        # (4) find in longer DLL with all unique values
        dll = DLL()
        for i in range(10):
            dll.push(i)

        node = dll.find(0)
        self.assertIsInstance(node, Node)
        self.assertIs(dll.head, node)
        self.assertIsNone(node.prev)
        self.assertEqual(0, node.value)
        self.assertEqual(1, node.next.value)

        node = dll.find(9)
        self.assertIsInstance(node, Node)
        self.assertIs(dll.tail, node)
        self.assertIsNone(node.next)
        self.assertEqual(9, node.value)
        self.assertEqual(8, node.prev.value)

        node = dll.find(4)
        self.assertIsInstance(node, Node)
        self.assertEqual(4, node.value)
        self.assertEqual(3, node.prev.value)
        self.assertEqual(5, node.next.value)

        node = dll.find(331)
        self.assertIsNone(node)

        # (5) find first instance in longer DLL with duplicated values
        for i in range(9, 0, -1):  # DLL will be 0, 1, ..., 9, 9, 8, ..., 0
            dll.push(i)

        node = dll.find(0)  # should find head 0, not tail 0
        self.assertIsInstance(node, Node)
        self.assertIs(dll.head, node)
        self.assertIsNone(node.prev)
        self.assertEqual(0, node.value)
        self.assertEqual(1, node.next.value)

        node = dll.find(9)  # should find first 9
        self.assertIsInstance(node, Node)
        self.assertEqual(9, node.value)
        self.assertEqual(8, node.prev.value)
        self.assertEqual(9, node.next.value)

        node = dll.find(4)  # should find first 4
        self.assertIsInstance(node, Node)
        self.assertEqual(4, node.value)
        self.assertEqual(3, node.prev.value)
        self.assertEqual(5, node.next.value)

        node = dll.find(331)
        self.assertIsNone(node)

    def test_find_all(self):
        # (1) find_all in empty DLL
        dll = DLL()
        nodes = dll.find_all(331)
        self.assertEqual([], nodes)

        # (2) find_all existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        nodes = dll.find_all(0)
        self.assertIsInstance(nodes, List)
        self.assertEqual(1, len(nodes))
        self.assertEqual(0, nodes[0].value)
        self.assertIsNone(nodes[0].next)
        self.assertIsNone(nodes[0].prev)

        # (3) find non-existing value in single-node DLL
        nodes = dll.find_all(331)
        self.assertEqual([], nodes)

        # (4) find_all in longer DLL with all unique values
        dll = DLL()
        for i in range(10):
            dll.push(i)

        nodes = dll.find_all(0)
        self.assertIsInstance(nodes, List)
        self.assertEqual(1, len(nodes))
        self.assertIs(dll.head, nodes[0])
        self.assertIsNone(nodes[0].prev)
        self.assertEqual(0, nodes[0].value)
        self.assertEqual(1, nodes[0].next.value)

        nodes = dll.find_all(9)
        self.assertIsInstance(nodes, List)
        self.assertEqual(1, len(nodes))
        self.assertIs(dll.tail, nodes[0])
        self.assertIsNone(nodes[0].next)
        self.assertEqual(9, nodes[0].value)
        self.assertEqual(8, nodes[0].prev.value)

        nodes = dll.find_all(4)
        self.assertIsInstance(nodes, List)
        self.assertEqual(1, len(nodes))
        self.assertEqual(4, nodes[0].value)
        self.assertEqual(3, nodes[0].prev.value)
        self.assertEqual(5, nodes[0].next.value)

        nodes = dll.find_all(331)
        self.assertEqual([], nodes)

        # (5) find all instances in longer DLL with duplicated values
        for i in range(9, -1, -1):  # DLL will be 0, 1, ..., 9, 9, 8, ..., 0
            dll.push(i)

        nodes = dll.find_all(0)
        self.assertIsInstance(nodes, List)
        self.assertEqual(2, len(nodes))
        self.assertIs(dll.head, nodes[0])
        self.assertIsNone(nodes[0].prev)
        self.assertEqual(0, nodes[0].value)
        self.assertEqual(1, nodes[0].next.value)
        self.assertIs(dll.tail, nodes[1])
        self.assertIsNone(nodes[1].next)
        self.assertEqual(0, nodes[1].value)
        self.assertEqual(1, nodes[1].prev.value)

        nodes = dll.find_all(9)
        self.assertIsInstance(nodes, List)
        self.assertEqual(2, len(nodes))
        self.assertEqual(9, nodes[0].value)
        self.assertEqual(8, nodes[0].prev.value)
        self.assertEqual(9, nodes[0].next.value)
        self.assertEqual(9, nodes[1].value)
        self.assertEqual(9, nodes[1].prev.value)
        self.assertEqual(8, nodes[1].next.value)

        nodes = dll.find_all(4)
        self.assertIsInstance(nodes, List)
        self.assertEqual(2, len(nodes))
        self.assertEqual(4, nodes[0].value)
        self.assertEqual(3, nodes[0].prev.value)
        self.assertEqual(5, nodes[0].next.value)
        self.assertEqual(4, nodes[1].value)
        self.assertEqual(5, nodes[1].prev.value)
        self.assertEqual(3, nodes[1].next.value)

        nodes = dll.find_all(331)
        self.assertEqual([], nodes)

    def test_remove(self):

        # (1) remove from empty DLL
        dll = DLL()
        result = dll.remove(331)
        self.assertFalse(result)

        # (2) remove existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        result = dll.remove(0)
        self.assertTrue(result)
        self.check_dll([], dll)  # if failure here, see (2)

        # (3) remove non-existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        result = dll.remove(331)
        self.assertFalse(result)
        self.check_dll([0], dll)  # if failure here, see (3)

        # (4) remove from longer DLL with all unique values
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)

        to_remove = [1, 4, 7, 5, 6, 3, 2, 9, 0, 8]
        for i in range(10):
            result = dll.remove(to_remove[i])
            self.assertTrue(result)
            result = dll.remove(331)
            self.assertFalse(result)

            lst.remove(to_remove[i])
            self.check_dll(lst, dll)  # if failure here, see (4)

        # (5) remove first instance in longer DLL with duplicated values
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)
        for i in range(9, -1, -1):  # DLL will be 0, 1, ..., 9, 9, 8, ..., 0
            dll.push(i)
            lst.append(i)

        to_remove = [1, 4, 7, 5, 6, 3, 2, 9, 0, 8]
        for i in range(10):
            result = dll.remove(to_remove[i])
            self.assertTrue(result)
            result = dll.remove(331)
            self.assertFalse(result)

            lst.remove(to_remove[i])
            self.check_dll(lst, dll)  # if failure here, see (5)

        # (6) sanity check after deletions
        lst = list(range(9, -1, -1))
        self.check_dll(lst, dll)  # if failure here, see (6)

    def test_remove_all(self):

        # (1) remove all from empty DLL
        dll = DLL()
        count = dll.remove_all(331)
        self.assertEqual(0, count)

        # (2) remove existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        count = dll.remove_all(0)
        self.assertEqual(1, count)
        self.check_dll([], dll)  # if failure here, see (2)

        # (3) remove non-existing value in single-node DLL
        dll = DLL()
        dll.push(0)
        count = dll.remove_all(331)
        self.assertEqual(0, count)
        self.check_dll([0], dll)  # if failure here, see (3)

        # (4) remove from longer DLL with all unique values
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)

        to_remove = [1, 4, 7, 5, 6, 3, 2, 9, 0, 8]
        for i in range(10):
            count = dll.remove_all(to_remove[i])
            self.assertEqual(1, count)
            count = dll.remove_all(331)
            self.assertEqual(0, count)

            lst.remove(to_remove[i])
            self.check_dll(lst, dll)  # if failure here, see (4)

        # (5) remove all in longer DLL with duplicated values
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)
        for i in range(9, -1, -1):  # DLL will be 0, 1, ..., 9, 9, 8, ..., 0
            dll.push(i)
            lst.append(i)

        to_remove = [1, 4, 7, 5, 6, 3, 2, 9, 0, 8]
        for i in range(10):
            count = dll.remove_all(to_remove[i])
            self.assertEqual(2, count)
            count = dll.remove_all(331)
            self.assertEqual(0, count)

            lst.remove(to_remove[i])
            lst.remove(to_remove[i])  # remove both instances
            self.check_dll(lst, dll)  # if failure here, see (5)

        # (6) sanity check empty list after all deletions
        self.check_dll([], dll)  # if failure here, see (6)

    def test_reverse(self):

        # (1) reverse empty DLL
        dll = DLL()
        dll.reverse()
        self.check_dll([], dll)  # if failure here, see (1)

        # (2) reverse single-node DLL
        dll = DLL()
        dll.push(0)
        dll.reverse()
        self.check_dll([0], dll)  # if failure here, see (2)

        # (3) reverse longer DLL
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)
        old_head, old_tail = dll.head, dll.tail
        dll.reverse()
        new_head, new_tail = dll.head, dll.tail
        lst.reverse()

        self.check_dll(lst, dll)
        self.assertIs(new_head, old_tail)
        self.assertIs(new_tail, old_head)

        # (4) reverse palindrome DLL
        dll = DLL()
        lst = []
        for i in range(10):
            dll.push(i)
            lst.append(i)
        for i in range(9, -1, -1):
            dll.push(i)
            lst.append(i)
        old_head, old_tail = dll.head, dll.tail
        dll.reverse()
        new_head, new_tail = dll.head, dll.tail
        lst.reverse()

        self.check_dll(lst, dll)
        self.assertIs(new_head, old_tail)
        self.assertIs(new_tail, old_head)


class GitTests(unittest.TestCase):
    def test_basic_commit(self):
        git = Git()
        self.assertIsNone(git.get_current_commit())
        commits = ["Initial commit", "Second commit", "Third commit"]

        for commit in commits:
            git.commit(commit)
            self.assertEqual(git.get_current_commit(), commit)

    # Test with no branches
    def test_basic_forward_backward(self):
        git = Git()
        self.assertIsNone(git.get_current_commit())
        git.backwards()
        self.assertIsNone(git.get_current_commit())
        git.forward()

        commits = ["Initial commit", "Second commit", "Third commit"]

        for commit in commits:
            git.commit(commit)

        self.assertEqual(git.get_current_commit(),  "Third commit")

        git.backwards()
        self.assertEqual(git.get_current_commit(),  "Second commit")
        
        git.backwards()
        self.assertEqual(git.get_current_commit(),  "Initial commit")

        git.backwards()
        self.assertEqual(git.get_current_commit(),  "Initial commit")

        git.forward()
        self.assertEqual(git.get_current_commit(),  "Second commit")

        git.backwards()
        self.assertEqual(git.get_current_commit(),  "Initial commit")

        git.forward()
        self.assertEqual(git.get_current_commit(),  "Second commit")
        git.forward()
        self.assertEqual(git.get_current_commit(),  "Third commit")
        git.forward()
        self.assertEqual(git.get_current_commit(),  "Third commit")
        git.backwards()

        with self.assertRaises(Exception):
            git.commit("Should throw as it is not last commit")
        git.forward()
        git.commit("Should work")

    def test_branches(self):
        git = Git()
        self.assertIsNone(git.get_current_commit())
        commits = ["Initial commit", "Second commit", "Third commit"]
        for commit in commits:
            git.commit(commit)

        # Create branch from end commit
        git.checkout_branch("new_feature")

        # Commit to branch
        git.commit("New feature branch commit")
        git.backwards()
        self.assertEqual(git.get_current_commit(), "Third commit")

        # Checks currently selected branch has not changed
        self.assertEqual(git.get_current_branch_name(), "new_feature")

        git.backwards()
        self.assertEqual(git.get_current_commit(), "Second commit")

        git.forward()
        self.assertEqual(git.get_current_commit(), "Third commit")

        git.forward()
        self.assertEqual(git.get_current_commit(), "New feature branch commit")

        git.commit("Second feature branch commit")
        self.assertEqual(git.get_current_commit(), "Second feature branch commit")

        git.backwards()
        git.backwards()
        # Now on last main branch commit
        self.assertEqual(git.get_current_commit(), "Third commit")
        git.forward()
        self.assertEqual(git.get_current_commit(), "New feature branch commit")
        git.forward()
        self.assertEqual(git.get_current_commit(), "Second feature branch commit")
        
        # Checkout main
        git.checkout_branch("main")
        self.assertEqual(git.get_current_commit(), "Third commit")
        git.commit("Fourth commit on main branch")
        self.assertEqual(git.get_current_commit(), "Fourth commit on main branch")

        git.backwards()
        git.backwards()
        self.assertEqual(git.get_current_commit(), "Second commit")

        git.forward()
        git.forward()
        self.assertEqual(git.get_current_commit(), "Fourth commit on main branch")

        git.checkout_branch("new_feature")
        self.assertEqual(git.get_current_commit(), "Second feature branch commit")

        # Create nested branch to middle commit
        git.backwards()
        git.checkout_branch("one_more_branch")

        self.assertIsNone(git.get_current_commit())

        git.backwards()
        self.assertEqual(git.get_current_commit(), "New feature branch commit")

        git.forward()
        self.assertIsNone(git.get_current_commit())
        self.assertEqual(git.get_current_branch_name(), "one_more_branch")

        git.commit("Nested branch")
        git.backwards()
        git.backwards()
        git.backwards()
        git.forward()
        git.forward()
        git.forward()
        self.assertEqual(git.get_current_commit(), "Nested branch")
        self.assertEqual(git.get_current_branch_name(), "one_more_branch")

        git.checkout_branch("new_feature")
        self.assertEqual(git.get_current_commit(), "Second feature branch commit")
        self.assertEqual(git.get_current_branch_name(), "new_feature")

        git.checkout_branch("main")
        self.assertEqual(git.get_current_commit(), "Fourth commit on main branch")
        self.assertEqual(git.get_current_branch_name(), "main")

    # Testing checkout branches - Not included for grading
    def test_branch_simple(self):
        git = Git()

        self.assertRaises(Exception,git.checkout_branch, "new_branch")
        self.assertIsNone(git.get_current_commit())
        self.assertEqual(git.get_current_branch_name(), "main")     

        git.checkout_branch("main")
        self.assertIsNone(git.get_current_commit())
        self.assertEqual(git.get_current_branch_name(), "main")   

        git = Git()
        commits = ["Initial commit", "Second commit", "Third commit"]
        for commit in commits:
            git.commit(commit)

        # Create branch from end commit
        git.checkout_branch("new_feature")
        self.assertEqual(git.get_current_branch_name(), "new_feature")

        # After branch creation, head should be none
        self.assertIsNone(git.get_current_commit())

        # Commit to branch
        git.commit("New feature branch commit")
        self.assertEqual(git.get_current_commit(), "New feature branch commit")
        self.assertEqual(git.get_current_branch_name(), "new_feature")

        git.commit("Final commit")
        self.assertEqual(git.get_current_commit(), "Final commit")
        self.assertEqual(git.get_current_branch_name(), "new_feature")

        git.checkout_branch('main')
        self.assertEqual(git.get_current_commit(), "Third commit")
        self.assertEqual(git.get_current_branch_name(), "main")
        git.forward()
        self.assertEqual(git.get_current_commit(), "Third commit")

    # Comprehensive tests for branches and commit - Not included for grading
    def test_multiple_branches(self):
        branches = ["third_branch", "main", "fourth_branch","second_branch"]
        commits = ["first_commit", "second_commit", "third_commit", "fourth_commit"]

        git = Git()

        for commit in commits:
            git.commit("main_" + commit)

        git.checkout_commit("main_third_commit")
        git.checkout_branch("second_branch")

        for commit in commits:
            git.commit("second_branch_" + commit)
        
        git.checkout_commit("second_branch_second_commit")
        git.checkout_branch("third_branch")
        for commit in commits:
            git.commit("third_branch_" + commit)

        git.checkout_branch("fourth_branch")
        for commit in commits:
            git.commit("fourth_branch_" + commit)

        for branch in branches:
            git.checkout_branch(branch)
            self.assertEqual(git.get_current_commit(), branch + "_fourth_commit")
            self.assertEqual(git.get_current_branch_name(), branch)
        
        git.checkout_commit("main_first_commit")
        self.assertEqual(git.get_current_commit(), "main_first_commit")
        self.assertEqual(git.get_current_branch_name(), "main")

    # Test checking out commits - Not included for grading
    def test_basic_checkout_commit(self):
        git = Git()
        self.assertIsNone(git.get_current_commit())
        commits = ["Initial commit", "Second commit", "Third commit"]

        for commit in commits:
            git.commit(commit)

        self.assertRaises(Exception, git.checkout_commit, "Non existent commit")

        git.checkout_commit("Initial commit")
        self.assertEqual(git.get_current_commit(),  "Initial commit")

        git.checkout_commit("Third commit")
        self.assertEqual(git.get_current_commit(),  "Third commit")

        git.checkout_commit("Third commit")
        self.assertEqual(git.get_current_commit(),  "Third commit")

        git.commit("Fourth commit")
        self.assertEqual(git.get_current_commit(),  "Fourth commit")
        git.checkout_commit("Third commit")
        self.assertEqual(git.get_current_commit(),  "Third commit")
        

if __name__ == '__main__':
    unittest.main()
