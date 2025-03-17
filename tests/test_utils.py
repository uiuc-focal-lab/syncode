# Custom assertion methods to handle long lists
class CustomAssertMixin:
    def assertInWithLimit(self, member, container, msg=None):
        """Assert that member is in container, with limited output if container is too long."""
        if member not in container:
            if len(container) <= 50:
                self.assertIn(member, container, msg)
            else:
                sample = list(container)[:10]
                self.fail(f"{repr(member)} not found in list with {len(container)} items. First 10 items: {sample}")
    
    def assertTrueWithLimit(self, expr, items, container, msg=None):
        """Assert that expression is true, with limited output for long containers."""
        if not expr:
            if len(container) <= 50:
                self.assertTrue(expr, msg)
            else:
                sample = list(container)[:10]
                self.fail(f"Assertion failed for items {items}. List has {len(container)} items. First 10 items: {sample}")
                
    def assertGreaterWithLimit(self, a, b, container, msg=None):
        """Assert a > b with limited output for the container."""
        if not (a > b):
            if len(container) <= 50:
                self.assertGreater(a, b, msg)
            else:
                sample = list(container)[:10]
                self.fail(f"{a} not greater than {b}. List has {len(container)} items. First 10 items: {sample}")