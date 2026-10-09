"""Accepted authored patches must remain separate from authored merged PR counts."""
import copy
import json
import sys
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from profile_data import DataError, LANDED_COMMITS, public_landed_commits


class PublicCommitClient:
    def __init__(self, mutate=None):
        self.calls = []
        self.mutate = mutate

    def request(self, url):
        self.calls.append(url)
        parsed = urlsplit(url)
        assert parsed.scheme == 'https' and parsed.netloc == 'api.github.com'
        for _, repo, sha, _ in LANDED_COMMITS:
            base = f'/repos/{repo}'
            if parsed.path == base:
                kind = 'repository'
                result = {'full_name': repo, 'private': False, 'default_branch': 'main'}
            elif parsed.path == f'{base}/commits/{sha}':
                kind = 'commit'
                result = {'sha': sha, 'html_url': f'https://github.com/{repo}/commit/{sha}',
                          'author': {'login': 'Miko997'}, 'commit': {'message': 'DISCARDED_MESSAGE'},
                          'files': [{'patch': 'DISCARDED_PATCH'}]}
            elif parsed.path == f'{base}/compare/{sha}...main':
                kind = 'compare'
                assert parsed.query == 'per_page=1'
                result = {'status': 'ahead', 'behind_by': 0, 'merge_base_commit': {'sha': sha},
                          'files': [{'patch': 'DISCARDED_COMPARE_PATCH'}]}
            else:
                continue
            if self.mutate:
                self.mutate(kind, result)
            return result
        raise AssertionError('Unexpected endpoint: ' + url)


class LandedCommitTests(unittest.TestCase):
    def test_complete_verification_retains_only_public_evidence_fields(self):
        client = PublicCommitClient()
        result = public_landed_commits(client, 'Miko997')
        self.assertEqual(len(result), 2)
        self.assertEqual(len(client.calls), 6)
        for item in result:
            self.assertEqual(set(item), {'repo', 'sha', 'url', 'author', 'default_branch', 'default_branch_verified'})
            self.assertTrue(item['default_branch_verified'])
        self.assertNotIn('DISCARDED', json.dumps(result))
        self.assertTrue(all('/repos/' in url for url in client.calls))

    def test_nonpublic_repository_is_rejected_before_commit_access(self):
        client = PublicCommitClient(lambda kind, result: result.update(private=True) if kind == 'repository' else None)
        with self.assertRaises(DataError):
            public_landed_commits(client, 'Miko997')
        self.assertEqual(len(client.calls), 1)

    def test_wrong_author_or_commit_identity_is_rejected(self):
        for replacement in ({'author': {'login': 'someone-else'}}, {'author': None},
                            {'sha': '0' * 40}, {'html_url': 'https://example.com/'}):
            def mutate(kind, result):
                if kind == 'commit':
                    result.update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(DataError):
                public_landed_commits(PublicCommitClient(mutate), 'Miko997')

    def test_branch_ancestry_must_be_positive_and_exact(self):
        for replacement in ({'status': 'behind'}, {'status': 'diverged'}, {'behind_by': 1},
                            {'merge_base_commit': {'sha': '0' * 40}}):
            def mutate(kind, result):
                if kind == 'compare':
                    result.update(replacement)
            with self.subTest(replacement=replacement), self.assertRaises(DataError):
                public_landed_commits(PublicCommitClient(mutate), 'Miko997')

    def test_identical_default_branch_commit_is_valid(self):
        client = PublicCommitClient(lambda kind, result: result.update(status='identical') if kind == 'compare' else None)
        self.assertEqual(len(public_landed_commits(client, 'Miko997')), 2)

    def test_failed_verification_does_not_return_partial_evidence(self):
        client = PublicCommitClient()
        request = client.request
        def fail_second_repository(url):
            if LANDED_COMMITS[1][1] in url:
                raise DataError('API unavailable')
            return request(url)
        client.request = fail_second_repository
        with self.assertRaises(DataError):
            public_landed_commits(client, 'Miko997')


if __name__ == '__main__':
    unittest.main()
