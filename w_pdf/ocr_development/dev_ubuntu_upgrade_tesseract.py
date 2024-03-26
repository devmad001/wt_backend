"""

ERROR:
Traceback (most recent call last):
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_exec/tesseract.py", line 407, in generate_pdf
    p = run(args_tesseract, stdout=PIPE, stderr=STDOUT, timeout=timeout, check=True)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/subprocess/__init__.py", line 63, in run
    proc = subprocess_run(args, env=env, check=check, **kwargs)
  File "/usr/lib/python3.10/subprocess.py", line 526, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['tesseract', '-l', 'eng', '-c', 'textonly_pdf=1', '/tmp/ocrmypdf.io.n79juaia/000001_ocr.png', '/tmp/ocrmypdf.io.n79juaia/000001_ocr_tess', 'pdf', 'txt']' died with <Signals.SIGKILL: 9>.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/ubuntu/wt/w_test/../w_pdf/ocr_development/test_ocr.py", line 32, in test_run_this_function
    is_good=call_test_run_with_test_files()
  File "/home/ubuntu/wt/w_test/../w_pdf/ocr_development/test_ocr.py", line 106, in call_test_run_with_test_files
    meta=local_run_ocr(test_file,output_filename)
  File "/home/ubuntu/wt/w_test/../w_pdf/ocr_development/test_ocr.py", line 72, in local_run_ocr
    meta=interface_pdfocr(input_filename,output_filename)
  File "/home/ubuntu/wt/w_pdf/ocr_model.py", line 58, in interface_pdfocr
    ocrmypdf.ocr(input_pdf, output_pdf, language=language,rotate_pages=True, deskew=True, force_ocr=True, jobs=jobs)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/api.py", line 359, in ocr
    return run_pipeline(options=options, plugin_manager=plugin_manager, api=True)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_sync.py", line 409, in run_pipeline
    optimize_messages = exec_concurrent(context, executor)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_sync.py", line 286, in exec_concurrent
    executor(
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_concurrent.py", line 86, in __call__
    self._execute(
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/builtin_plugins/concurrency.py", line 138, in _execute
    result = future.result()
  File "/usr/lib/python3.10/concurrent/futures/_base.py", line 451, in result
    return self.__get_result()
  File "/usr/lib/python3.10/concurrent/futures/_base.py", line 403, in __get_result
    raise self._exception
  File "/usr/lib/python3.10/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_sync.py", line 224, in exec_page_sync
    (ocr_out, text_out) = ocr_engine_textonly_pdf(ocr_image_out, page_context)
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_pipeline.py", line 750, in ocr_engine_textonly_pdf
    ocr_engine.generate_pdf(
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/builtin_plugins/tesseract_ocr.py", line 264, in generate_pdf
    tesseract.generate_pdf(
  File "/home/ubuntu/.local/lib/python3.10/site-packages/ocrmypdf/_exec/tesseract.py", line 419, in generate_pdf
    raise SubprocessOutputError() from e
ocrmypdf.exceptions.SubprocessOutputError


"""