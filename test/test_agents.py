# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""测试任务管理代理。"""

import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agents.agent import root_agent

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase):
    """测试任务管理代理的用例。"""

    def setUp(self):
        """为测试方法设置环境。"""
        self.session = session_service.create_session(
            app_name="TaskManagementAgent",
            user_id="test_user",
        )
        self.user_id = "test_user"
        self.session_id = self.session.id

        self.runner = Runner(
            app_name="TaskManagementAgent",
            agent=None,
            artifact_service=artifact_service,
            session_service=session_service,
        )

    def _run_agent(self, agent, query):
        """帮助方法，运行代理并获取最终响应。"""
        self.runner.agent = agent
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = list(
            self.runner.run(
                user_id=self.user_id, session_id=self.session_id, new_message=content
            )
        )

        last_event = events[-1]
        final_response = "".join(
            [part.text for part in last_event.content.parts if part.text]
        )
        return final_response

    def test_root_agent_current_tasks(self):
        """测试根代理能够查询当前任务列表。"""
        query = "我当前有什么任务"
        response = self._run_agent(root_agent, query)
        print(f"测试响应: {response}")
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()

    # 手动运行测试
    # testagent = TestAgents()
    # testagent.setUp()
    # testagent.test_root_agent_current_tasks()