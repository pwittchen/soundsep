help:
	@echo "help             shows help"
	@echo "clean_models     cleans models"
	@echo "clean_output     cleans output"
	@echo "clean            cleans everything"
clean_models:
	rm -rf pretrained_models || true
clean_output:
	rm -rf output || true
clean:
	rm -rf pretrained_models || true
	rm -rf output || true
