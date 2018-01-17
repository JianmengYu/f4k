for i=1:20
    A = rand(i*100,100,100);
    B = rand(5,5,5);
    tic;
    for j=1:(i*100)
        for k=1:5
            conv2(squeeze(A(j,:,:)),squeeze(B(k,:,:)));
        end
    end
    toc
end