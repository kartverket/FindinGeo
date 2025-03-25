from langchain_core.outputs import LLMResult, RunInfo
from langchain_huggingface import HuggingFaceEndpoint
import json


# https://github.com/langchain-ai/langchain/issues/18321
class CustomHuggingFaceEndpoint(HuggingFaceEndpoint):
    def generate_prompt(
        self,
        prompts,
        stop = None,
        callbacks = None,
        **kwargs,
    ):
        prompt_strings = [p.to_string() for p in prompts]
        return self.generate(prompt_strings, stop=stop, callbacks=callbacks, **kwargs)

    def _generate_helper(
        self,
        prompts,
        stop,
        run_managers,
        new_arg_supported,
        **kwargs,
    ):
        try:
            output = (
                self._generate(
                    prompts,
                    stop=stop,
                    # TODO: support multiple run managers
                    run_manager=run_managers[0] if run_managers else None,
                    **kwargs,
                )
                if new_arg_supported
                else self._generate(prompts, stop=stop)
            )
        except BaseException as e:
            for run_manager in run_managers:
                run_manager.on_llm_error(e, response=LLMResult(generations=[]))
            raise e
        flattened_outputs = output.flatten()
        for manager, flattened_output in zip(run_managers, flattened_outputs):
            manager.on_llm_end(flattened_output)
        if run_managers:
            output.run = [
                RunInfo(run_id=run_manager.run_id) for run_manager in run_managers
            ]
        return output
    def _call(
        self,
        prompt: str,
        stop = None,
        run_manager= None,
        **kwargs,
    ) -> str:
        """Call out to HuggingFace Hub's inference endpoint."""
        invocation_params = self._invocation_params(stop, **kwargs)
        if self.streaming:
            completion = ""
            for chunk in self._stream(prompt, stop, run_manager, **invocation_params):
                completion += chunk.text
            return completion
        else:
            invocation_params["stop"] = invocation_params[
                "stop_sequences"
            ]  # porting 'stop_sequences' into the 'stop' argument
            response = self.client.post(
                json={"inputs": prompt, "parameters": invocation_params},
                stream=False,
                task=self.task,
            )
            try:
                response_text = json.loads(response.decode())[0]["generated_text"]
            except KeyError:
                response_text = json.loads(response.decode())["generated_text"]

            # Maybe the generation has stopped at one of the stop sequences:
            # then we remove this stop sequence from the end of the generated text
            if invocation_params["stop_sequences"]:
              for stop_seq in invocation_params["stop_sequences"]:
                  if response_text[-len(stop_seq) :] == stop_seq:
                      response_text = response_text[: -len(stop_seq)]
            return response_text


  
    def _invocation_params(
        self, runtime_stop, **kwargs
    ):
        params = {**self._default_params, **kwargs}
        if isinstance(params["stop_sequences"], list):
            params["stop_sequences"] = params["stop_sequences"] + (runtime_stop or [])
        return params