from zipkin.zipkin_data import ZipkinId


class ZipkinTestHelpers(object):
    def assertZipkinDataEquals(self, a, b, msg=None):
        for field in ['sampled', 'flags']:
            self.assertEqual(getattr(a, field), getattr(b, field), msg)
        for field in ['trace_id', 'span_id', 'parent_span_id']:
            a_id = getattr(a, field)
            b_id = getattr(b, field)
            if a_id is not None:
                self.assertIsInstance(a_id, ZipkinId)
                if b_id is not None:
                    self.assertIsInstance(b_id, ZipkinId)
                    self.assertEqual(a_id.get_binary(), b_id.get_binary())
                    return
            self.assertEqual(a_id, b_id)
