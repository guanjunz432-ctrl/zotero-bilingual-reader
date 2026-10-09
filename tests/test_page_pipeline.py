import unittest
from page_pipeline import process_pages
from bilingual_reader import TranslationFormatError

class PipelineTest(unittest.TestCase):
    def test_invalid_json_does_not_stop_later_pages(self):
        calls=[]
        def process(page,attempt):
            calls.append((page,attempt))
            if page==2:raise TranslationFormatError('invalid JSON')
        result=process_pages([1,2,3],process,lambda p:False,lambda m:None)
        self.assertEqual(calls,[(1,1),(2,1),(3,1),(2,2),(2,3)])
        self.assertEqual(result['completed_pages'],[1,3])
        self.assertEqual(result['status'],'partial')
        self.assertEqual(list(result['failed_pages']),['2'])
    def test_successful_retry_after_forward_pass(self):
        calls=[]
        def process(page,attempt):
            calls.append((page,attempt))
            if page==1 and attempt==1:raise TranslationFormatError('bad JSON')
        result=process_pages([1,2,3],process,lambda p:p==2,lambda m:None)
        self.assertEqual(calls,[(1,1),(3,1),(1,2)])
        self.assertEqual(result['status'],'complete')
    def test_user_stop_is_respected_before_retry(self):
        class Stop:
            value=False
            def is_set(self):return self.value
        stop=Stop();calls=[]
        def process(page,attempt):calls.append(page);stop.value=True
        result=process_pages([1,2],process,lambda p:False,lambda m:None,stop)
        self.assertEqual(calls,[1]);self.assertEqual(result['status'],'stopped')

if __name__=='__main__':unittest.main()
